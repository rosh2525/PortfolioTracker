from django.db import models
from django.db.models import Q

from apps.assets.models import Asset
from apps.core.models import UserOwnedModel


class StockAnalysis(UserOwnedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        INSUFFICIENT_DATA = "INSUFFICIENT_DATA", "Insufficient data"
        FAILED = "FAILED", "Failed"

    class Rating(models.TextChoices):
        VERY_BEARISH = "VERY_BEARISH", "Very Bearish"
        BEARISH = "BEARISH", "Bearish"
        NEUTRAL = "NEUTRAL", "Neutral"
        BULLISH = "BULLISH", "Bullish"
        VERY_BULLISH = "VERY_BULLISH", "Very Bullish"

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="stock_analyses")
    task_id = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    rating = models.CharField(max_length=24, choices=Rating.choices, null=True, blank=True)
    signal_score = models.PositiveSmallIntegerField(null=True, blank=True)
    data_coverage = models.PositiveSmallIntegerField(default=0)
    summary = models.TextField(blank=True, default="")
    factors = models.JSONField(default=dict, blank=True)
    metrics_snapshot = models.JSONField(default=dict, blank=True)
    bull_case = models.JSONField(default=list, blank=True)
    bear_case = models.JSONField(default=list, blank=True)
    catalysts = models.JSONField(default=list, blank=True)
    risks = models.JSONField(default=list, blank=True)
    citations = models.JSONField(default=list, blank=True)
    data_timestamp = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    gemini_model = models.CharField(max_length=80, blank=True, default="")
    prompt_version = models.CharField(max_length=32, blank=True, default="v1")
    error_code = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "asset", "-created_at"], name="idx_analysis_owner_asset"),
            models.Index(fields=["owner", "status", "-created_at"], name="idx_analysis_owner_status"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(signal_score__isnull=True) | Q(signal_score__gte=0, signal_score__lte=100),
                name="analysis_signal_score_0_100",
            ),
            models.CheckConstraint(
                condition=Q(data_coverage__gte=0, data_coverage__lte=100),
                name="analysis_coverage_0_100",
            ),
            models.UniqueConstraint(
                fields=["owner", "asset"],
                condition=Q(status__in=["PENDING", "RUNNING"]),
                name="unique_active_stock_analysis",
            ),
        ]
