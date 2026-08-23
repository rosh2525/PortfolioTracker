import uuid

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.assets.models import Asset

from .models import StockAnalysis
from .serializers import StockAnalysisSerializer
from .tasks import generate_stock_analysis_task


class StockAnalysisThrottle(UserRateThrottle):
    scope = "stock_analysis"


def _eligible(asset: Asset) -> bool:
    ticker = asset.ticker or ""
    return asset.type == Asset.AssetType.STOCK and ticker.upper().endswith((".NS", ".BO"))


class StockAnalysisView(APIView):
    @staticmethod
    def _asset(request, asset_id: str) -> Asset:
        return get_object_or_404(Asset, pk=asset_id, owner=request.user)

    @staticmethod
    def _unsupported() -> Response:
        return Response(
            {"detail": "AI stock analysis supports Indian STOCK assets with .NS or .BO tickers."}, status=400
        )

    def get(self, request, asset_id: str) -> Response:
        asset = self._asset(request, asset_id)
        if not _eligible(asset):
            return self._unsupported()
        analyses = StockAnalysis.objects.filter(owner=request.user, asset=asset).select_related("asset")
        analysis = analyses.filter(status__in=[StockAnalysis.Status.PENDING, StockAnalysis.Status.RUNNING]).first()
        if analysis is None:
            analysis = analyses.filter(
                status__in=[StockAnalysis.Status.COMPLETED, StockAnalysis.Status.INSUFFICIENT_DATA],
                expires_at__gt=timezone.now(),
            ).first()
        if analysis is None:
            analysis = analyses.first()
        return Response(StockAnalysisSerializer(analysis).data if analysis else None)

    def post(self, request, asset_id: str) -> Response:
        asset = self._asset(request, asset_id)
        if not _eligible(asset):
            return self._unsupported()
        if not settings.GEMINI_API_KEY:
            return Response({"detail": "AI analysis is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        now = timezone.now()
        cached = (
            StockAnalysis.objects.filter(
                owner=request.user,
                asset=asset,
                status__in=[StockAnalysis.Status.COMPLETED, StockAnalysis.Status.INSUFFICIENT_DATA],
                expires_at__gt=now,
            )
            .select_related("asset")
            .first()
        )
        if cached:
            return Response({"cached": True, "analysis": StockAnalysisSerializer(cached).data})
        active = StockAnalysis.objects.filter(
            owner=request.user, asset=asset, status__in=[StockAnalysis.Status.PENDING, StockAnalysis.Status.RUNNING]
        ).first()
        if active:
            return Response(
                {"cached": False, "analysis_id": active.pk, "task_id": active.task_id, "status": active.status},
                status=202,
            )
        throttle = StockAnalysisThrottle()
        if not throttle.allow_request(request, self):
            raise Throttled(wait=throttle.wait(), detail="Daily AI analysis limit reached. Try again tomorrow.")
        task_id = str(uuid.uuid4())
        try:
            with transaction.atomic():
                analysis = StockAnalysis.objects.create(owner=request.user, asset=asset, task_id=task_id)
                transaction.on_commit(
                    lambda: generate_stock_analysis_task.apply_async(
                        args=[str(analysis.pk), request.user.pk], task_id=task_id
                    )
                )
        except IntegrityError:
            analysis = StockAnalysis.objects.get(
                owner=request.user, asset=asset, status__in=[StockAnalysis.Status.PENDING, StockAnalysis.Status.RUNNING]
            )
            task_id = analysis.task_id
        return Response(
            {"cached": False, "analysis_id": analysis.pk, "task_id": task_id, "status": analysis.status}, status=202
        )
