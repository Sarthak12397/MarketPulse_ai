from pydantic import BaseModel
from datetime import datetime
from typing import List


class CandleDto(BaseModel):
    open_time_utc:  datetime   # matches .NET RawCandleDto exactly
    close_time_utc: datetime   # matches .NET RawCandleDto exactly
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float


class SignalRequest(BaseModel):
    symbol:    str
    timeframe: str
    candles:   List[CandleDto]