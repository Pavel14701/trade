from typing import Any
import okx.Account as Account # type: ignore
import okx.MarketData as MarketData # type: ignore
import okx.Trade as Trade # type: ignore
from datetime import datetime, timedelta
from api.data import OkxApiData, OrderDataOutput
from configs.provider import ConfigsProvider
from cache.redis_cache import RedisCache


class OkxApi:
    def __init__(self, configs:OkxApiData):
        settings = ConfigsProvider()
        self.api_settings = settings.load_api_okx_configs()
        self.user_settings = settings.load_user_settings()
        self.key = 'contracts_prices'
        self.configs = configs
        self.cache = RedisCache(configs)
        self.marketDataAPI:MarketData.MarketAPI = self.__create_marketAPI()
        self.accountAPI:Account.AccountAPI = self.__create_accountAPI()
        self.tradeAPI:Trade.TradeAPI = self.__create_trade_api()


    def __create_accountAPI(self) -> Account.AccountAPI:
        return Account.AccountAPI(
            api_key = self.api_settings.api_key,
            api_secret_key = self.api_settings.secret_key,
            passphrase = self.api_settings.passphrase,
            use_server_time = False,
            flag = self.api_settings.flag
        )

    def __create_trade_api(self) -> Trade.TradeAPI:
        return Trade.TradeAPI(
            api_key= self.api_settings.api_key,
            api_secret_key = self.api_settings.secret_key,
            passphrase = self.api_settings.passphrase,
            use_server_time = False,
            flag = self.api_settings.flag
        )

    def __create_marketAPI(self) -> MarketData.MarketAPI:
        return MarketData.MarketAPI(flag=self.api_settings.flag)

    def __check_result(self, result:dict) -> dict[str, Any]:
        if result['code'] != '0':
            raise ValueError(f'Error, code: {result['code']}')
        return result

    def __check_pos_side(self):
        if self.configs.posSide == 'long':
                    side = 'sell'
        elif self.configs.posSide == 'short':
                    side = 'buy'
        return side

    def get_market_data(self, data:OkxApiData) -> dict:
        result = self.marketDataAPI.get_candlesticks(
                instId=self.configs.instId,
                after=data.after,
                before=data.before,
                bar=self.configs.timeframe,
                limit=data.lengths
            )
        return self.__check_result(result)

    def get_market_data_history(self, data:OkxApiData) -> dict:
        result = self.marketDataAPI.get_history_candlesticks(
                instId=self.configs.instId,
                after=data.after,
                before=data.before,
                bar=self.configs.timeframe,
                limit=data.lengths
            )
        return self.__check_result(result)

    def check_balance(self) -> float:
        result = self.accountAPI.get_account_balance()
        self.__check_result(result)
        return float(result["data"][0]["details"][0]["availBal"])

    def set_leverage_inst(self) -> int:
        result = self.accountAPI.set_leverage(
            instId=self.configs.instId,
            lever=self.user_settings.leverage,
            mgnMode=self.user_settings.mgnMode
        )
        result = self.__check_result(result)
        return self.user_settings.leverage

    def set_leverage_short_long(self, data:OkxApiData) -> None:
        result = self.accountAPI.set_leverage(
            instId = self.configs.instId,
            lever = self.user_settings.leverage,
            posSide = data.posSide,
            mgnMode = self.user_settings.mgnMode
        )
        result = self.__check_result(result)

    def set_trading_mode(self) -> None:
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        result = self.__check_result(result)

    def check_contract_price(self) -> None:
        result = self.accountAPI.get_instruments(instType="SWAP")
        result = self.__check_result(result)
        if self.key:
            self.cache.send_redis_command(result, self.key)
        raise ValueError('Key is not setted')

    def check_contract_price_cache(self, data: OkxApiData) -> float:
        result = self.cache.load_message_from_cache()
        if result is None:
            raise ValueError("No data found in cache")
        try:
            return float(next(instrument['ctVal'] for instrument in result['data'] if instrument['instId'] == data.instId))
        except (StopIteration, KeyError, TypeError) as e:
            raise ValueError("Instrument ID not found or invalid data format") from e


    def check_instrument_price(self, data:OkxApiData) -> float:
        result = self.marketDataAPI.get_ticker(data.instId)
        self.__check_result(result)
        return float(result['data'][0]['last'])

    def construct_market_order(self, side:str) -> OrderDataOutput:
        result = self.tradeAPI.place_order(
            instId = self.configs.instId,
            tdMode = self.user_settings.mgnMode,
            side = self.__check_pos_side(),
            posSide = self.configs.posSide,
            ordType = 'market',
            sz = str(self.configs.size)
        )
        self.__check_result(result)
        return OrderDataOutput(
            result = result,
            orderId = result['data'][0]['ordId'], 
            outTime =  datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        )


    def construct_stoploss_order(self) -> str:
        result = self.tradeAPI.place_algo_order(
            instId = self.configs.instId,
            tdMode = self.user_settings.mgnMode,
            side = self.__check_pos_side(),
            posSide = self.configs.posSide,
            ordType = 'conditional',
            sz = str(self.configs.size),
            slTriggerPx = str(self.configs.slPrice),
            slOrdPx = '-1',
            slTriggerPxType = 'last'
        )
        self.__check_result(result)
        return result['data'][0]['ordId']

    def change_stoploss_order(self, slPrice:float, orderId:str) -> None:
        result = self.tradeAPI.amend_algo_order(
            instId=self.configs.instId,
            algoId=orderId,
            newSlTriggerPx=str(slPrice)
        )
        self.__check_result(result)
        return result

    def construct_takeprofit_order(self) -> str:
        result = self.tradeAPI.place_algo_order(
            instId = self.configs.instId,
            tdMode = self.user_settings.mgnMode,
            side = self.__check_pos_side(),
            posSide = self.configs.posSide,
            ordType = 'conditional',
            sz = self.configs.size,
            tpTriggerPx = self.configs.tpPrice,
            tpOrdPx = '-1',
            tpTriggerPxType = 'last'
        )
        self.__check_result(result)
        return result['data'][0]['ordId']

    def change_takeprofit_order(self, tpPrice:float, orderId:str):
        result = self.tradeAPI.amend_algo_order(
            instId = self.configs.instId,
            algoId = orderId,
            newTpTriggerPx = str(tpPrice)
        )
        self.__check_result(result)
        return result

    def construct_limit_order(self, price) -> OrderDataOutput:
        side = self.__check_pos_side()
        result = self.tradeAPI.place_order(
            instId = self.configs.instId,
            tdMode = self.user_settings.mgnMode,
            side = side,
            posSide = self.configs.posSide,
            ordType = 'limit',
            px = price,
            sz = str(self.configs.size)
        )
        self.__check_result(result)
        return OrderDataOutput(
            result = result,
            orderId = result['data'][0]['ordId'], 
            outTime =  datetime.fromtimestamp(int(result['outTime'])/1000000) + timedelta(hours=3)
        )

    def calculate_posSize(self, contract_price:float|int) -> float:
        if self.user_settings.leverage is not None and self.user_settings.risk is not None and self.configs.slPrice is not None: 
            return ((self.check_balance()) * self.user_settings.leverage * self.user_settings.risk) / self.configs.slPrice #type: ignore
        raise ValueError('Check leverage, risk, and slPrice configs for posSize calculating')

    def check_position(self, ordId) -> float:
        result = self.tradeAPI.get_order(
            instId=self.configs.instId,
            ordId=ordId)
        self.__check_result(result)
        return float(result["data"][0]["avgPx"])

    def get_all_order_list(self) -> dict:
        result = self.tradeAPI.get_order_list()
        self.__check_result(result)
        return result

    def get_all_opened_positions(self) -> dict:
        result = self.accountAPI.get_positions()
        self.__check_result(result)
        return result

    def get_history(self) -> dict:
        result = self.tradeAPI.get_fills(instType = 'SWAP')
        self.__check_result(result)
        return result