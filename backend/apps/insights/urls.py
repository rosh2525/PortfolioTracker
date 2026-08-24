from django.urls import path

from .views import StockAnalysisView

urlpatterns = [path("assets/<uuid:asset_id>/stock-analysis/", StockAnalysisView.as_view(), name="stock-analysis")]
