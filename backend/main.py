from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from . import price_sync, storage
from .models import Dividend, DividendIn, Holding, HoldingIn

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()


# ---------- Holdings ----------

@app.get("/api/holdings", response_model=list[Holding])
def get_holdings():
    return storage.list_holdings()


@app.post("/api/holdings", response_model=Holding)
def post_holding(holding: HoldingIn):
    return storage.create_holding(holding.model_dump())


@app.put("/api/holdings/{holding_id}", response_model=Holding)
def put_holding(holding_id: str, holding: HoldingIn):
    updated = storage.update_holding(holding_id, holding.model_dump())
    if updated is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return updated


@app.delete("/api/holdings/{holding_id}")
def remove_holding(holding_id: str):
    if not storage.delete_holding(holding_id):
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"ok": True}


# ---------- Dividends ----------

@app.get("/api/dividends", response_model=list[Dividend])
def get_dividends():
    return storage.list_dividends()


@app.post("/api/dividends", response_model=Dividend)
def post_dividend(dividend: DividendIn):
    return storage.create_dividend(dividend.model_dump())


@app.put("/api/dividends/{dividend_id}", response_model=Dividend)
def put_dividend(dividend_id: str, dividend: DividendIn):
    updated = storage.update_dividend(dividend_id, dividend.model_dump())
    if updated is None:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return updated


@app.delete("/api/dividends/{dividend_id}")
def remove_dividend(dividend_id: str):
    if not storage.delete_dividend(dividend_id):
        raise HTTPException(status_code=404, detail="Dividend not found")
    return {"ok": True}


# ---------- Sync ----------

@app.post("/api/sync")
def sync_prices():
    try:
        return price_sync.sync()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Sync failed: {e}")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
