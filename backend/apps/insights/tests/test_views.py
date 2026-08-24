from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.assets.models import Asset
from apps.insights.models import StockAnalysis


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username="analyst", password="pass")


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(username="other", password="pass")


@pytest.fixture
def client(user):
    result = APIClient()
    result.force_authenticate(user)
    return result


@pytest.fixture
def stock(user):
    return Asset.objects.create(owner=user, name="Reliance", ticker="RELIANCE.NS", type="STOCK", currency="INR")


@pytest.mark.django_db
def test_authentication_required(stock):
    assert APIClient().get(f"/api/assets/{stock.id}/stock-analysis/").status_code == 401


@pytest.mark.django_db
def test_owner_isolation(client, other_user):
    asset = Asset.objects.create(owner=other_user, name="TCS", ticker="TCS.NS", type="STOCK")
    assert client.get(f"/api/assets/{asset.id}/stock-analysis/").status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(("asset_type", "ticker"), [("ETF", "NIFTYBEES.NS"), ("STOCK", "AAPL"), ("STOCK", None)])
def test_unsupported_assets(client, user, asset_type, ticker):
    asset = Asset.objects.create(owner=user, name="Unsupported", ticker=ticker, type=asset_type)
    assert client.post(f"/api/assets/{asset.id}/stock-analysis/").status_code == 400


@pytest.mark.django_db
def test_missing_key_is_service_unavailable(client, stock, settings):
    settings.GEMINI_API_KEY = ""
    response = client.post(f"/api/assets/{stock.id}/stock-analysis/")
    assert response.status_code == 503
    assert response.data["detail"] == "AI analysis is not configured."


@pytest.mark.django_db
@pytest.mark.parametrize("analysis_status", ["COMPLETED", "INSUFFICIENT_DATA"])
def test_reuses_24_hour_result(client, user, stock, settings, analysis_status):
    settings.GEMINI_API_KEY = "test-key"
    analysis = StockAnalysis.objects.create(
        owner=user, asset=stock, status=analysis_status, expires_at=timezone.now() + timedelta(hours=1)
    )
    response = client.post(f"/api/assets/{stock.id}/stock-analysis/")
    assert response.status_code == 200
    assert response.data["cached"] is True
    assert response.data["analysis"]["id"] == str(analysis.id)


@pytest.mark.django_db
def test_get_preserves_recent_success_after_failed_refresh(client, user, stock):
    successful = StockAnalysis.objects.create(
        owner=user, asset=stock, status="COMPLETED", expires_at=timezone.now() + timedelta(hours=1)
    )
    StockAnalysis.objects.create(owner=user, asset=stock, status="FAILED", error_code="PROVIDER_TIMEOUT")
    response = client.get(f"/api/assets/{stock.id}/stock-analysis/")
    assert response.status_code == 200
    assert response.data["id"] == str(successful.id)


@pytest.mark.django_db
def test_active_job_is_deduplicated(client, user, stock, settings):
    settings.GEMINI_API_KEY = "test-key"
    analysis = StockAnalysis.objects.create(owner=user, asset=stock, status="RUNNING", task_id="task-1")
    response = client.post(f"/api/assets/{stock.id}/stock-analysis/")
    assert response.status_code == 202
    assert response.data["analysis_id"] == analysis.id
    assert StockAnalysis.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_enqueues_new_analysis(client, stock, settings):
    settings.GEMINI_API_KEY = "test-key"
    with patch("apps.insights.views.generate_stock_analysis_task.apply_async") as enqueue:
        response = client.post(f"/api/assets/{stock.id}/stock-analysis/")
    assert response.status_code == 202
    assert response.data["task_id"]
    enqueue.assert_called_once()
