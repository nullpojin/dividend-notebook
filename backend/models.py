from typing import Literal

from pydantic import BaseModel


class HoldingIn(BaseModel):
    code: str = ""
    name: str
    shares: float
    costPrice: float
    currentPrice: float
    isFund: bool = False
    taxStatus: Literal["taxable", "nisa"] = "taxable"


class Holding(HoldingIn):
    id: str


class DividendIn(BaseModel):
    name: str
    amount: float
    date: str


class Dividend(DividendIn):
    id: str
