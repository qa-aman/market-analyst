from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    symbols: list[str]
    query_type: str = "single"  # "single" | "multi"


class CompareRequest(BaseModel):
    symbols: list[str]  # exactly 2


class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: str


class StockListResponse(BaseModel):
    stocks: list[StockInfo]
