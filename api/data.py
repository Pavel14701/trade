from pydantic import BaseModel # type: ignore
from datetime import datetime
import pandas as pd
from typing import Optional


class OkxApiData(BaseModel):
    instId = Optional[str]
    timeframe = Optional[str]
    lengths = Optional[int]
    before = Optional[str]
    after = Optional[str]
    posSide = Optional[str]
    slPrice = Optional[int|float]
    tpPrice = Optional[int|float]
    size = Optional[int]
    key = Optional[str]
    channel = Optional[str]
    data = Optional[pd.DataFrame]


class OrderDataOutput(BaseModel):
    result = dict
    orderId = str|int
    outTime = datetime