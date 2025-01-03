import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel #type: ignore
from datetime import datetime, timedelta


class PriceData(BaseModel):
    date: list[datetime]
    open: list[float|Decimal]
    high: list[float|Decimal]
    low: list[float|Decimal]
    close: list[float|Decimal]
    volume: list[float|Decimal|int]
    volume_usdt: list[float|Decimal|int]


class PriceDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return PriceDataFrame
    
    @property
    def date(self) -> pd.Series:
        return self['date']

    @property
    def open(self) -> pd.Series:
        return self['open']

    @property
    def high(self) -> pd.Series:
        return self['high']

    @property
    def low(self) -> pd.Series:
        return self['low']

    @property
    def close(self) -> pd.Series:
        return self['close']

    @property
    def volume(self) -> pd.Series:
        return self['volume']

    @property
    def volume_usdt(self) -> pd.Series:
        return self['volume_usdt']


def prepare_data_to_dataframe(result: dict[str, str]) -> PriceData:
    dates, opens, highs, lows, closes, volumes, volumes_usdt = [], [], [], [], [], [], []
    for item in result["data"]:
        dates.append(datetime.fromtimestamp(int(item[0]) / 1000) + timedelta(hours=3))
        opens.append(float(item[1]))
        highs.append(float(item[2]))
        lows.append(float(item[3]))
        closes.append(float(item[4]))
        volumes.append(float(item[6]))
        volumes_usdt.append(float(item[7]))
    return PriceData(
        date=dates,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        volume=volumes,
        volume_usdt=volumes_usdt
    )


def create_dataframe(price_data:PriceData) -> pd.DataFrame:
    data_dict = price_data.model_dump(by_alias=True)
    df = PriceDataFrame(data_dict)
    df.set_index(df.date, inplace=True)
    return df.sort_values(by='date', ascending=True)