from __future__ import annotations

import csv
import uuid
from pathlib import Path
from threading import Lock

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HOLDINGS_CSV = DATA_DIR / "holdings.csv"
DIVIDENDS_CSV = DATA_DIR / "dividends.csv"

HOLDINGS_FIELDS = ["id", "code", "name", "shares", "costPrice", "currentPrice"]
DIVIDENDS_FIELDS = ["id", "name", "amount", "date"]

_lock = Lock()


def _ensure_csv(path: Path, fields: list[str]) -> None:
    if not path.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def _read_rows(path: Path, fields: list[str]) -> list[dict]:
    _ensure_csv(path, fields)
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_rows(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _new_id() -> str:
    return uuid.uuid4().hex


# ---------- Holdings ----------

def list_holdings() -> list[dict]:
    rows = _read_rows(HOLDINGS_CSV, HOLDINGS_FIELDS)
    for r in rows:
        r["shares"] = float(r["shares"])
        r["costPrice"] = float(r["costPrice"])
        r["currentPrice"] = float(r["currentPrice"])
    return rows


def create_holding(data: dict) -> dict:
    with _lock:
        rows = _read_rows(HOLDINGS_CSV, HOLDINGS_FIELDS)
        row = {"id": _new_id(), **data}
        rows.append(row)
        _write_rows(HOLDINGS_CSV, HOLDINGS_FIELDS, rows)
        return row


def update_holding(holding_id: str, data: dict) -> dict | None:
    with _lock:
        rows = _read_rows(HOLDINGS_CSV, HOLDINGS_FIELDS)
        updated = None
        for r in rows:
            if r["id"] == holding_id:
                r.update(data)
                updated = r
                break
        if updated is not None:
            _write_rows(HOLDINGS_CSV, HOLDINGS_FIELDS, rows)
        return updated


def delete_holding(holding_id: str) -> bool:
    with _lock:
        rows = _read_rows(HOLDINGS_CSV, HOLDINGS_FIELDS)
        new_rows = [r for r in rows if r["id"] != holding_id]
        if len(new_rows) == len(rows):
            return False
        _write_rows(HOLDINGS_CSV, HOLDINGS_FIELDS, new_rows)
        return True


# ---------- Dividends ----------

def list_dividends() -> list[dict]:
    rows = _read_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS)
    for r in rows:
        r["amount"] = float(r["amount"])
    return rows


def create_dividend(data: dict) -> dict:
    with _lock:
        rows = _read_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS)
        row = {"id": _new_id(), **data}
        rows.append(row)
        _write_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS, rows)
        return row


def update_dividend(dividend_id: str, data: dict) -> dict | None:
    with _lock:
        rows = _read_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS)
        updated = None
        for r in rows:
            if r["id"] == dividend_id:
                r.update(data)
                updated = r
                break
        if updated is not None:
            _write_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS, rows)
        return updated


def delete_dividend(dividend_id: str) -> bool:
    with _lock:
        rows = _read_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS)
        new_rows = [r for r in rows if r["id"] != dividend_id]
        if len(new_rows) == len(rows):
            return False
        _write_rows(DIVIDENDS_CSV, DIVIDENDS_FIELDS, new_rows)
        return True
