from datetime import datetime
from pydantic import BaseModel #type: ignore

class InstrumentTimeframeDataSchema(BaseModel):
    timestamp: datetime
    instrument: str 
    timeframe: str
    open: float 
    close: float 
    high: float 
    low: float 
    volume: float 
    volume_usdt: float

    class Config: 
        orm_mode = True


class InstrumentTimeframeOrderData(BaseModel):
    orderId = str
    orderType = str
    status = bool
    orderVolume = int|float
    tpOrderVolume = int|float
    slOrderVolume = int|float
    balance = int|float
    instId = str
    leverage = int
    sideOfTrade = str
    enterPrice = float|int
    time = datetime
    tpOrderId = str|int|None
    tpPrice = float|int|None
    slOrderId = str|int|None
    slPrice = int|float|None
    history_of_trade = dict|None

    class Config:
        orm_mode = True


# TO DO 
class HistoryTradeJSON(BaseModel):
    key1: str
    key2: int
    key3: bool

    class Config:
        orm_mode = True
