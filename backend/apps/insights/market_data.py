import math
from datetime import datetime
from typing import Any

import yfinance as yf


def _number(value: Any, digits: int = 4) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return round(result, digits) if math.isfinite(result) else None


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


class YahooFinanceProvider:
    """Read-only, public market data used for personal/research analysis."""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)

    def get_fundamentals(self) -> dict[str, Any]:
        info = self.stock.get_info() or {}
        result = {
            "trailing_pe": _number(info.get("trailingPE")),
            "forward_pe": _number(info.get("forwardPE")),
            "price_to_book": _number(info.get("priceToBook")),
            "market_cap": _number(info.get("marketCap"), 0),
            "revenue_growth": _number(info.get("revenueGrowth")),
            "earnings_growth": _number(info.get("earningsGrowth")),
            "profit_margin": _number(info.get("profitMargins")),
            "operating_margin": _number(info.get("operatingMargins")),
            "return_on_equity": _number(info.get("returnOnEquity")),
            "debt_to_equity": _number(info.get("debtToEquity")),
        }
        result["has_financial_snapshot"] = sum(value is not None for value in result.values()) >= 3
        return result

    @staticmethod
    def _return(series: Any, months: int) -> float | None:
        if series is None or len(series) < 2:
            return None
        cutoff = series.index[-1] - __import__("pandas").DateOffset(months=months)
        window = series.loc[series.index >= cutoff]
        if len(window) < 2 or not window.iloc[0]:
            return None
        return _number((window.iloc[-1] / window.iloc[0] - 1) * 100, 2)

    def get_price_momentum(self) -> dict[str, Any]:
        benchmark = "^NSEI" if self.ticker.endswith(".NS") else "^BSESN"
        stock_history = self.stock.history(period="7mo", auto_adjust=True)
        benchmark_history = yf.Ticker(benchmark).history(period="7mo", auto_adjust=True)
        stock_close = stock_history.get("Close")
        benchmark_close = benchmark_history.get("Close")
        returns = {f"return_{months}m": self._return(stock_close, months) for months in (1, 3, 6)}
        benchmark_returns = {months: self._return(benchmark_close, months) for months in (1, 3, 6)}
        relative: dict[str, float | None] = {}
        for months in (1, 3, 6):
            stock_return = returns[f"return_{months}m"]
            benchmark_return = benchmark_returns[months]
            relative[f"relative_{months}m"] = (
                _number(stock_return - benchmark_return, 2)
                if stock_return is not None and benchmark_return is not None
                else None
            )
        volatility = None
        if stock_close is not None and len(stock_close) > 2:
            volatility = _number(stock_close.pct_change().dropna().std() * math.sqrt(252) * 100, 2)
        return {"benchmark": benchmark, **returns, **relative, "annualized_volatility": volatility}

    def get_earnings_context(self) -> dict[str, Any]:
        import pandas as pd

        result: dict[str, Any] = {
            "latest_reported_at": None,
            "eps_estimate": None,
            "eps_actual": None,
            "eps_surprise_percent": None,
            "next_earnings_date": None,
        }
        dates = self.stock.get_earnings_dates(limit=8)
        if dates is not None and not dates.empty:
            index_timezone = getattr(dates.index, "tz", None)
            now = pd.Timestamp.now(tz=index_timezone) if index_timezone else pd.Timestamp.now()
            past = dates[dates.index <= now].sort_index(ascending=False)
            if not past.empty:
                row = past.iloc[0]
                result.update(
                    latest_reported_at=_iso(past.index[0]),
                    eps_estimate=_number(row.get("EPS Estimate")),
                    eps_actual=_number(row.get("Reported EPS")),
                    eps_surprise_percent=_number(row.get("Surprise(%)")),
                )
        calendar = self.stock.get_calendar() or {}
        earnings_date = calendar.get("Earnings Date")
        if isinstance(earnings_date, (list, tuple)) and earnings_date:
            earnings_date = earnings_date[0]
        result["next_earnings_date"] = _iso(earnings_date)
        return result
