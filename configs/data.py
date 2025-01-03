from pydantic import BaseModel # type: ignore

class SystemConfigs(BaseModel):
    db_uri: str

class UserConfigs(BaseModel):
    timeframes: tuple[str]
    instIds: tuple[str]
    leverage: int
    risk: float
    mgnMode: str

class CacheConfigs(BaseModel):
    host = str
    port = int
    db = int
    celery_db = int

class AvslConfigs(BaseModel):
    lengthsFast: int
    lengthsSlow: int
    lenT: int
    standDiv: float
    offset: int

class RsiCloudsConfigs(BaseModel):
    rsi_period = int
    rsi_scalar = int
    rsi_drift = int
    rsi_offset = int
    rsi_mamode = str
    rsi_talib_config = bool
    macd_fast = int
    macd_slow = int
    macd_signal = int
    macd_offset = int
    calc_data = str
    macd_talib_config = bool


class AdxConfigs(BaseModel):
    timeperiod = int
    lenghts_sig = int
    adxr_lenghts = int|None
    scalar = int
    talib = bool
    tvmode = bool
    mamode = str
    drift = int
    offset = int
    trigger = int


class OkxApiConfigs(BaseModel):
    api_key = str
    secret_key = str
    passphrase = str
    flag = bool