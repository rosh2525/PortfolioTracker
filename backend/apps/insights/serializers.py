from rest_framework import serializers

from .models import StockAnalysis


class StockAnalysisSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    ticker = serializers.CharField(source="asset.ticker", read_only=True)

    class Meta:
        model = StockAnalysis
        fields = [
            "id",
            "asset",
            "asset_name",
            "ticker",
            "task_id",
            "status",
            "rating",
            "signal_score",
            "data_coverage",
            "summary",
            "factors",
            "metrics_snapshot",
            "bull_case",
            "bear_case",
            "catalysts",
            "risks",
            "citations",
            "data_timestamp",
            "expires_at",
            "gemini_model",
            "prompt_version",
            "error_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
