import pandas as pd
import numpy as np
import matplotlib.pyplot as plt #type: ignore 
from matplotlib.axes import Axes #type: ignore
import pandas_ta as ta #type: ignore
from indicators.data import PriceDataFrame
from configs.provider import ConfigsProvider
from configs.data import AvslConfigs


class AVSLIndicator:
    def __init__ (self, data:PriceDataFrame):
        self.settings:AvslConfigs = ConfigsProvider().load_avsl_settings()
        self.data = data

    def calculate_avsl(self, return_all:bool|None=None) -> pd.Series:
        vwma_f:pd.Series = ta.vwma(self.data.close, self.data.volume, length=self.settings.lengthsFast)
        vwma_s:pd.Series = ta.vwma(self.data.close, self.data.volume, length=self.settings.lengthsSlow)
        vpc:pd.Series = vwma_s - ta.sma(self.data.close, length=self.settings.lengthsSlow)
        vpr:pd.Series = vwma_f / ta.sma(self.data.close, length=self.settings.lengthsFast)
        vm:pd.Series = ta.sma(
            self.data.volume, length=self.settings.lengthsFast
            ) / ta.sma(
                self.data.volume, length=self.settings.lengthsSlow
            )
        vpci:pd.Series = vpc * vpr * vm
        del(vwma_f, vwma_s)
        PriceV = self.__price_fun(vpc, vpr, vpci)
        DeV:pd.Series = self.settings.standDiv * vpci * vm
        avsl:pd.Series = ta.sma(self.data.low - PriceV + DeV, length=self.settings.lengthsSlow)
        return avsl if return_all else avsl.iloc[-1]

    def __price_fun(self, vpc: pd.Series, vpr: pd.Series, vpci: pd.Series) -> np.ndarray:
        lenV = np.where(
            np.isnan(vpci), 0, np.round(np.abs(vpci - 3)) * (vpc < 0) + np.round(vpci + 3) * (vpc >= 0)
        ).astype(int)
        VPCc = np.where(
            (vpc > -1) & (vpc < 0), -1, np.where((vpc < 1) & (vpc >= 0), 1, vpc)
        )
        Price = np.where(
            lenV > 0, np.sum(
                np.divide(
                    self.data['Low'].rolling(window=int(lenV)).apply(lambda x: np.sum(x / VPCc / vpr)), vpr
                ), axis=1
            ), self.data['Low']
        )
        return np.where(lenV > 0, Price / lenV / 100, Price)

    def create_avsl_vizualization(self) -> None:
        avsl = self.calculate_avsl(True)
        fig:plt.Figure
        ax:Axes
        fig, ax = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        ax.plot(self.data.index, self.data.close, label='Цена закрытия', color='blue')
        ax.plot(self.data.index, avsl, label='AVSL', color='red')
        ax.legend()
        ax.set_title('Визуализация AVSL')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        plt.show()