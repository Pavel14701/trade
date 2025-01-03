import matplotlib.pyplot as plt #type: ignore 
from matplotlib.axes import Axes #type: ignore 
import pandas as pd
import pandas_ta as ta #type: ignore 
from typing import Any
from configs.provider import ConfigsProvider
from indicators.data import PriceDataFrame

class ADXTrend:
    def __init__(self, data: PriceDataFrame):
        self.configs = ConfigsProvider().load_adx_configs()
        self.data = data

    def calculate_adx(self) -> Any:
        self.adx = ta.adx(
            self.data.high, self.data.low, self.data.close, 
            self.configs.timeperiod, self.configs.lenghts_sig, self.configs.adxr_lenghts, self.configs.scalar,
            self.configs.talib, self.configs.tvmode, self.configs.mamode, self.configs.drift, self.configs.offset
        )
        adx:pd.Series = self.adx[f'ADX_{self.configs.timeperiod}']
        return adx.iloc[-1]


    def create_vizualization_adx(self):
        if self.adx is None:
            data = self.calculate_adx()
        fig:plt.figure
        ax1:Axes
        ax2:Axes
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax1.plot(self.data.index, self.data.close, label='Цена закрытия', color='blue')
        ax2.plot(self.data.index, self.adx[f'ADX_{self.configs.timeperiod}'], label='ADX', color='orange')
        ax1.legend()
        ax1.set_title('Визуализация ADX')
        ax1.set_xlabel('Дата')
        ax1.set_ylabel('Цена')
        plt.show()