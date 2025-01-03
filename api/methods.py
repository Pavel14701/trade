import pandas as pd
from datetime import datetime
from api.okx_api import OkxApi
from api.data import OkxApiData, OrderDataOutput 
from datasets.methods import PriceDbMethods
from datasets.data import InstrumentTimeframeOrderData


class PlaceOrders(OkxApi):    
    def __init__(self, configs:OkxApiData):
        super().__init__(configs)
        self.configs = configs

    def place_market_order(self) -> str:
        orderType = 'market'
        balance = self.check_balance()
        contract_price = self.check_contract_price_cache(self.configs)
        size = self.calculate_posSize(contract_price)
        result:OrderDataOutput = self.construct_market_order(self.configs.posSide)
        enter_price = self.check_position(result.orderId)
        data = InstrumentTimeframeOrderData(
            orderId = result.orderId,
            orderType = orderType,
            status = True,
            orderVolume = size,
            tpOrderVolume = size,
            slOrderVolume = size,
            balance = balance,
            instId = self.configs.instId,
            leverage = self.set_leverage_inst(),
            sideOfTrade = self.configs.posSide,
            enterPrice = enter_price,
            time = datetime.now(),
            tpOrderId = None if self.configs.tpPrice is None else self.construct_takeprofit_order(),
            tpPrice = self.configs.tpPrice,
            slOrderId = None if self.configs.slPrice is None else self.construct_stoploss_order(),
            slPrice = self.configs.slPrice
        )
        PriceDbMethods().save_new_order_data(data)
        return str(result['order_id'])

    def place_limit_order(self, price:float) -> str:
        orderType = 'market'
        balance = self.check_balance()
        contract_price = self.check_contract_price_cache(self.configs)
        size = self.calculate_posSize(contract_price)
        result:OrderDataOutput = self.construct_limit_order(price)
        data = InstrumentTimeframeOrderData(
            orderId = result.orderId,
            orderType = orderType,
            status = False,
            orderVolume = size,
            tpOrderVolume = size,
            slOrderVolume = size,
            balance = balance,
            instId = self.configs.instId,
            leverage = self.set_leverage_inst(),
            sideOfTrade = self.configs.posSide,
            enterPrice = price,
            time = datetime.now(),
            tpOrderId = None if self.configs.tpPrice is None else self.construct_takeprofit_order(),
            tpPrice = self.configs.tpPrice,
            slOrderId = None if self.configs.slPrice is None else self.construct_stoploss_order(),
            slPrice = self.configs.slPrice
        )
        PriceDbMethods().save_new_order_data(data)
        return str(result['order_id'])