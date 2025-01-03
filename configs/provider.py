import os
from dotenv import load_dotenv
from configs.data import UserConfigs, RsiCloudsConfigs, SystemConfigs, AvslConfigs, OkxApiConfigs, CacheConfigs


class ConfigsProvider:
    def __check(self, key:str) -> str:
        result = os.getenv(key)
        if result is None:
            raise ValueError(f'Key {key} is not setted')
        return result

    def load_system_settings(self) -> SystemConfigs:
        load_dotenv(dotenv_path='configs/system_configs.env')
        return SystemConfigs(
            db_uri=os.getenv('DB_URI')
        )

    def load_user_settings(self) -> UserConfigs:
        load_dotenv(dotenv_path='configs/configs_user.env')
        return UserConfigs(
            timeframe=tuple(self.__check('TIMEFRAMES').split(',')),
            instIds = tuple(self.__check('INSTIDS').split(',')),
            leverage = int(self.__check('LEVERAGE')),
            risk = float(self.__check('RISK')),
            mgnMode = str(self.__check('MGNMODE'))
        )

    def load_rsi_clouds_settings(self) -> RsiCloudsConfigs:
        load_dotenv(dotenv_path='configs/configs_rsi_clouds.env')
        return RsiCloudsConfigs(
            rsi_period = int(self.__check('RSI_LENGHTS')),
            rsi_scalar = int(self.__check('RSI_SCALAR')),
            rsi_drift = int(self.__check('RSI_DRIFT')),
            rsi_offset = int(self.__check('RSI_OFFSET')),
            rsi_mamode = str(self.__check('MA_MODE')),
            rsi_talib_config = bool(self.__check('RSI_TALIB_CONFIG')),
            macd_fast = int(self.__check('MACD_FAST')),
            macd_slow = int(self.__check('MACD_SLOW')),
            macd_signal = int(self.__check('MACD_SIGNAL')),
            macd_offset = int(self.__check('MACD_OFFSET')),
            calc_data = str(self.__check('CALC_DATA')),
            macd_talib_config = bool(self.__check('MACD_TALIB_CONFIG'))
        )

    def load_avsl_settings(self) -> AvslConfigs:
        load_dotenv(dotenv_path='configs/configs_avsl.env')
        return AvslConfigs(
            lenghtsFast = int(self.__check('LENGHTS_FAST')),
            lenghtsSlow = int(self.__check('LENGHTS_SLOW')),
            lenT = int(self.__check('LEN_T')),
            standDiv = float(self.__check('STAND_DIV')),
            offset = int(self.__check('OFFSET'))
        )

    def load_api_okx_configs(self) -> OkxApiConfigs:
        load_dotenv(dotenv_path='configs/configs_api_okx.env')
        return OkxApiConfigs(
            flag = bool(self.__check('FLAG')),
            api_key = self.__check('API_KEY'),
            passphrase = self.__check('PASSPHRASE'),
            secret_key = self.__check('SECRET_KEY'),
        )

    def load_cache_settings(self) -> CacheConfigs:
        load_dotenv(dotenv_path='configs/configs_cache.env')
        return CacheConfigs(
            host = self.__check('HOST'),
            port = int(self.__check('PORT')),
            db = int(self.__check('DB')),
            celery_db = int(self.__check('CELERY_DB'))
        )