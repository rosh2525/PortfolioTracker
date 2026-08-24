import pytest
from django.utils import timezone

from apps.insights.scoring import calculate_signal, has_enough_evidence, rating_for_score


@pytest.mark.parametrize(
    ("score", "rating"),
    [
        (0, "VERY_BEARISH"),
        (19, "VERY_BEARISH"),
        (20, "BEARISH"),
        (39, "BEARISH"),
        (40, "NEUTRAL"),
        (59, "NEUTRAL"),
        (60, "BULLISH"),
        (79, "BULLISH"),
        (80, "VERY_BULLISH"),
        (100, "VERY_BULLISH"),
    ],
)
def test_rating_boundaries(score, rating):
    assert rating_for_score(score) == rating


def test_server_weighting_and_missing_factor_normalisation():
    factors = {
        "fundamentals": {"score": 100, "available": True},
        "valuation": {"score": 0, "available": True},
        "earnings": {"score": 50, "available": True},
        "momentum": {"score": 100, "available": False},
        "news": {"score": 50, "available": True},
    }
    assert calculate_signal(factors) == (53, "NEUTRAL", 85)


def test_insufficient_evidence_rules():
    today = timezone.localdate().isoformat()
    sources = [{"domain": "a.test", "published_at": today}, {"domain": "b.test", "published_at": today}]
    assert not has_enough_evidence({"has_financial_snapshot": False}, sources, 100)
    assert not has_enough_evidence({"has_financial_snapshot": True}, sources[:1], 100)
    assert not has_enough_evidence({"has_financial_snapshot": True}, sources, 64)
    assert has_enough_evidence({"has_financial_snapshot": True}, sources, 65)
