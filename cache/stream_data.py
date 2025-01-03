import pandas as pd
from typing import NoReturn
from datasets.methods import PriceDbMethods
from indicators.data import prepare_data_to_dataframe, create_dataframe, PriceDataFrame
from api.okx_api import OkxApi, OkxApiData
from cache.redis_cache import RedisCache

class StreamData:
    def __init__(self, data: OkxApiData):
        if not data.instId or not data.timeframe:
            self.__error('InstId or timeframe is not set')
        self.api = OkxApi(data)
        self.cache = RedisCache(data)
        self.db = PriceDbMethods()
        self.data: OkxApiData = data

    def load_data(self, data: OkxApiData) -> pd.DataFrame:
        pr_data = prepare_data_to_dataframe(self.api.get_market_data_history(data))
        self.data.data = create_dataframe(pr_data)
        if self.data.data is not None:
            self.__save(self.data.data)
            self.cache.add_data_to_cache(PriceDataFrame(self.data.data))
            return self.data.data
        else:
            self.__error('Data is not set')

    def load_data_for_period(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        pr_data = prepare_data_to_dataframe(self.api.get_market_data_history(data=self.data))
        data_point = create_dataframe(pr_data)
        if data_point is not None:
            self.__save(data_point)
            return pd.concat([data, data_point], ignore_index=True)
        else:
            self.__error('Data point is not set')

    def __save(self, data: pd.DataFrame) -> None:
        instId:str = self.data.instId or self.__error('InstId is not set') #type: ignore
        timeframe:str = self.data.timeframe or self.__error('Timeframe is not set') #type: ignore
        self.db.add_data(
            instId=instId,
            timeframe=timeframe,
            data_list=self.db.dataframe_to_schema_list(PriceDataFrame(data), instId, timeframe)
        )

    def __error(self, message: str) -> NoReturn:
        raise ValueError(message)
