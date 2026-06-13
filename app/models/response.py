from pydantic import BaseModel
from typing import Optional


class SignalResponse(BaseModel):
    direction:        str            # "Long" | "Short" | "Neutral"
    confidence_score: float          # 0.0 - 1.0
    reasoning:        str
    entry_zone_low:   Optional[float] = None
    entry_zone_high:  Optional[float] = None
    stop_loss:        Optional[float] = None
    take_profit_one:  Optional[float] = None
    take_profit_two:  Optional[float] = None