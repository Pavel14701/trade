import pickle
import pandas as pd
from typing import Any, Optional, Dict
from redis import Redis
from configs.provider import ConfigsProvider
from cache.data import StreamDataConfigs
from indicators.data import PriceDataFrame

class RedisCache(Redis): 
    def __init__(self, configs:StreamDataConfigs):
        cache = ConfigsProvider().load_cache_settings()
        self.user_settings = ConfigsProvider().load_user_settings()
        self.configs = configs
        super().__init__(host=cache.host, port=cache.port, db=cache.db)

    def add_data_to_cache(self, data:PriceDataFrame) -> None:
        self.set(f'df_{self.configs.instId}_{self.configs.timeframe}', pickle.dumps(data))

    def load_data_from_cache(self) -> pd.DataFrame:
        if self.configs.instId is not None and self.configs.timeframe is not None:
            data:bytes = self.get(f'df_{self.configs.instId}_{self.configs.timeframe}') # type: ignore
            if data:
                return pd.DataFrame(pickle.loads(data))
            return pd.DataFrame()
        raise ValueError('timeframe or instId is not setted')

    def subscribe_to_redis_channel(self) -> None:
        if self.configs.channel:
            self.pubsub().subscribe(self.configs.channel)
            return
        raise ValueError(f'Channel not setted')

    def subscribe_to_redis_channels(self) -> None:
        for instId in self.user_settings.instIds:
            for timeframe in self.user_settings.timeframes:
                channel = f'channel_{instId}_{timeframe}'
                self.pubsub().subscribe(channel)

    def check_redis_message(self) -> Optional[Dict[str, str]]:
        message = self.pubsub().get_message()
        if message and message['type'] == 'message':
            return pickle.loads(message['data'])
        return None

    def send_redis_command(self, message: str, key: str) -> None:
        self.set(key, pickle.dumps(message))

    def publish_message(self, message: str) -> None:
        if self.configs.channel:
            self.publish(self.configs.channel, pickle.dumps(message)) # type: ignore
        raise ValueError(f'Channel not setted') 

    def load_message_from_cache(self) -> Optional[Any]:
        if self.configs.key is not None:
            value:bytes = self.get(self.configs.key) # type: ignore
            if value is not None:
                return pickle.loads(value)
        return None
