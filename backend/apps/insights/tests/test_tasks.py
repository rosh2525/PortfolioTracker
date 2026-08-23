from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.assets.models import Asset
from apps.insights.models import StockAnalysis
from apps.insights.tasks import generate_stock_analysis_task


@pytest.mark.django_db
def test_task_persists_completed_result(settings):
    user = get_user_model().objects.create_user(username="task-user")
    asset = Asset.objects.create(owner=user, name="Infosys", ticker="INFY.NS", type="STOCK")
    analysis = StockAnalysis.objects.create(owner=user, asset=asset)
    settings.GEMINI_MODEL = "gemini-test"
    result = SimpleNamespace(
        status="COMPLETED",
        rating="BULLISH",
        signal_score=70,
        data_coverage=100,
        payload={
            "summary": "Supported",
            "factors": {},
            "metrics_snapshot": {},
            "bull_case": [],
            "bear_case": [],
            "catalysts": [],
            "risks": [],
            "citations": [],
        },
    )
    with patch("apps.insights.tasks.StockThesisAgent") as agent:
        agent.return_value.run.return_value = result
        task_result = generate_stock_analysis_task.apply(args=[str(analysis.id), user.id]).get()
    analysis.refresh_from_db()
    assert task_result["status"] == "COMPLETED"
    assert analysis.signal_score == 70
    assert analysis.expires_at is not None


@pytest.mark.django_db
def test_task_stores_only_safe_error_code(settings):
    user = get_user_model().objects.create_user(username="failed-user")
    asset = Asset.objects.create(owner=user, name="Infosys", ticker="INFY.NS", type="STOCK")
    analysis = StockAnalysis.objects.create(owner=user, asset=asset)
    with patch("apps.insights.tasks.StockThesisAgent") as agent:
        agent.return_value.run.side_effect = RuntimeError("secret provider response")
        generate_stock_analysis_task.apply(args=[str(analysis.id), user.id]).get()
    analysis.refresh_from_db()
    assert analysis.status == "FAILED"
    assert analysis.error_code == "ANALYSIS_FAILED"
    assert "secret" not in analysis.error_code
