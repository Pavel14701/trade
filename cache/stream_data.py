import pandas as pd
from typing import Optional
from cache.data import StreamDataConfigs
from datasets.methods import PriceDbMethods
from cache.redis_cache import RedisCache
from indicators.data import prepare_data_to_dataframe


class StreamData():
    def __init__(self, data:StreamDataConfigs):
        OKXInfoFunctions.__init__(self, instId, timeframe, lenghts)
        self.data = data
        self.instId = data.instId
        self.timeframe = data.timeframe
        self.lenghts = lenghts
        self.channel = channel
        RedisCache.__init__(self, self.instId, self.timeframe, self.channel, self.key)

    def load_data(self) -> pd.DataFrame:
        prepared_df = prepare_many_data_to_append_db(self.get_market_data(self.lenghts))
        PriceDbMethods().add_data(
            instId = self.data.instId,
            timeframe = self.data.timeframe,
            data_list = 
        )
        self.add_data_to_cache(create_dataframe(prepared_df))

    def load_data_for_period(self, data:pd.DataFrame) -> pd.DataFrame:
        data = data.drop(data.index[:1])
        prepare_df = prepare_many_data_to_append_db(self.get_market_data(lengths=1))
        DataAllDatasets(self.Session, self.classes_dict, self.instId, self.timeframe)\
            .save_charts(prepare_df)
        df = pd.concat([data, create_dataframe(prepare_df)], ignore_index=True)
        print(df)
        return df
