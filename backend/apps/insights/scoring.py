from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

FACTOR_WEIGHTS = {
    "fundamentals": 25,
    "valuation": 20,
    "earnings": 20,
    "momentum": 15,
    "news": 20,
}


def rating_for_score(score: int) -> str:
    if score < 20:
        return "VERY_BEARISH"
    if score < 40:
        return "BEARISH"
    if score < 60:
        return "NEUTRAL"
    if score < 80:
        return "BULLISH"
    return "VERY_BULLISH"


def calculate_signal(factors: dict[str, Any]) -> tuple[int | None, str | None, int]:
    weighted_total = Decimal("0")
    coverage = 0
    for name, weight in FACTOR_WEIGHTS.items():
        factor = factors.get(name) or {}
        if not factor.get("available", True) or factor.get("score") is None:
            continue
        score = max(0, min(100, int(factor["score"])))
        weighted_total += Decimal(score * weight)
        coverage += weight
    if coverage == 0:
        return None, None, 0
    score = int((weighted_total / Decimal(coverage)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return score, rating_for_score(score), coverage


def has_enough_evidence(metrics: dict[str, Any], citations: list[dict[str, Any]], coverage: int) -> bool:
    cutoff = date.today() - timedelta(days=30)
    sources = set()
    for citation in citations:
        try:
            published_at = date.fromisoformat(str(citation.get("published_at"))[:10])
        except (TypeError, ValueError):
            continue
        if cutoff <= published_at <= date.today() + timedelta(days=1):
            sources.add(citation.get("source_key") or citation.get("domain"))
    sources.discard(None)
    return coverage >= 65 and bool(metrics.get("has_financial_snapshot")) and len(sources) >= 2
