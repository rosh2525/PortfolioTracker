import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .agent import PROMPT_VERSION, AnalysisProviderError, StockThesisAgent
from .models import StockAnalysis

logger = logging.getLogger(__name__)


def _safe_error(exc: Exception) -> tuple[str, bool]:
    if isinstance(exc, AnalysisProviderError):
        return exc.error_code, exc.transient
    name, message = type(exc).__name__.lower(), str(exc).lower()
    if "429" in message or "quota" in message or "resourceexhausted" in name:
        return "AI_QUOTA_LIMITED", True
    if "timeout" in name or "timed out" in message:
        return "PROVIDER_TIMEOUT", True
    if "yfinance" in name or "yahoo" in message:
        return "MARKET_DATA_UNAVAILABLE", True
    return "ANALYSIS_FAILED", False


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_stock_analysis_task(self, analysis_id: str, user_id: int) -> dict[str, object]:
    try:
        analysis = StockAnalysis.objects.select_related("asset").get(pk=analysis_id, owner_id=user_id)
    except StockAnalysis.DoesNotExist:
        return {"user_id": user_id, "analysis_id": analysis_id, "status": "NOT_FOUND"}
    analysis.status = StockAnalysis.Status.RUNNING
    analysis.error_code = ""
    analysis.save(update_fields=["status", "error_code", "updated_at"])
    try:
        result = StockThesisAgent(analysis.asset).run()
        now = timezone.now()
        for field, value in result.payload.items():
            setattr(analysis, field, value)
        analysis.status = result.status
        analysis.rating = result.rating
        analysis.signal_score = result.signal_score
        analysis.data_coverage = result.data_coverage
        analysis.data_timestamp = now
        analysis.expires_at = now + timedelta(hours=settings.STOCK_ANALYSIS_TTL_HOURS)
        analysis.gemini_model = settings.GEMINI_MODEL
        analysis.prompt_version = PROMPT_VERSION
        analysis.error_code = ""
        analysis.save()
    except Exception as exc:  # Provider SDK exception types vary by version.
        error_code, transient = _safe_error(exc)
        if transient and self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=30 * (2**self.request.retries)) from exc
        logger.warning("Stock analysis %s failed with %s", analysis_id, error_code)
        analysis.status = StockAnalysis.Status.FAILED
        analysis.error_code = error_code
        analysis.save(update_fields=["status", "error_code", "updated_at"])
    return {"user_id": user_id, "analysis_id": analysis_id, "status": analysis.status}
