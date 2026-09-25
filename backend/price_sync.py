from __future__ import annotations

import time
from datetime import date, timedelta

import yfinance as yf

from . import storage

TICKER_SUFFIX = ".T"  # Tokyo Stock Exchange
DIVIDEND_LOOKBACK_DAYS = 400
WITHHOLDING_TAX_RATE = 0.20315
REQUEST_DELAY_SECONDS = 1.0


def sync() -> dict:
    holdings_updated = []
    dividends_added = []
    skipped = []
    warnings = []
    errors = []

    existing_holdings = storage.list_holdings()
    existing_dividends = storage.list_dividends()
    today = date.today()
    lookback_start = today - timedelta(days=DIVIDEND_LOOKBACK_DAYS)

    def already_recorded(name: str, iso_date: str) -> bool:
        for d in existing_dividends:
            if d["name"] == name and d["date"] == iso_date:
                return True
        for d in dividends_added:
            if d["name"] == name and d["date"] == iso_date:
                return True
        return False

    first = True
    for h in existing_holdings:
        code = (h.get("code") or "").strip()
        if not code:
            skipped.append(h["name"])
            continue
        if not first:
            time.sleep(REQUEST_DELAY_SECONDS)
        first = False

        symbol = f"{code}{TICKER_SUFFIX}"
        ticker = yf.Ticker(symbol)

        try:
            new_price = float(ticker.fast_info["lastPrice"])
            old_price = h["currentPrice"]
            storage.update_holding(h["id"], {"currentPrice": new_price})
            holdings_updated.append({"name": h["name"], "code": code, "oldPrice": old_price, "newPrice": new_price})
        except Exception as e:
            errors.append(f"Price fetch failed for {h['name']} ({symbol}): {e}")

        try:
            series = ticker.dividends
            for ts, per_share in series.items():
                d = ts.date()
                if d < lookback_start or d > today:
                    continue
                iso_date = d.isoformat()
                gross = float(per_share) * h["shares"]
                tax_rate = 0.0 if h.get("taxStatus") == "nisa" else WITHHOLDING_TAX_RATE
                net = round(gross * (1 - tax_rate))
                if net <= 0:
                    continue
                if already_recorded(h["name"], iso_date):
                    continue
                storage.create_dividend({"name": h["name"], "amount": net, "date": iso_date})
                dividends_added.append({"name": h["name"], "date": iso_date, "amount": net, "estimated": True})
        except Exception as e:
            errors.append(f"Dividend fetch failed for {h['name']} ({symbol}): {e}")

    return {
        "holdingsUpdated": holdings_updated,
        "dividendsAdded": dividends_added,
        "skipped": skipped,
        "warnings": warnings,
        "errors": errors,
    }
