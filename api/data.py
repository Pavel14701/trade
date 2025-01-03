from pydantic import BaseModel # type: ignore
from datetime import datetime

class OkxApiData(BaseModel):
    instId = str|None
    timeframe = str|None
    lengths = int|None
    before = str|None
    after = str|None
    posSide = str|None
    
    slPrice = int|float|None
    tpPrice = int|float|None
    size = int|None


class OrderDataOutput(BaseModel):
    result = dict
    orderId = str|int
    outTime = datetime