from pydantic import BaseModel #type: ignore
from indicators.data import PriceDataFrame 

class StreamDataConfigs(BaseModel):
    instId = str|None
    timeframe = str|None
    lenghts = int|None
    key = str|None
    channel = str|None
    data = PriceDataFrame|None