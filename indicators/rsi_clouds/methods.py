import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.axes import Axes  # type: ignore
from typing import Any
import pandas_ta as ta  # type: ignore
from indicators.data import PriceDataFrame
from configs.provider import ConfigsProvider


class CloudsRsi:
    def __init__(self, data: PriceDataFrame, _type: str):
        self.configs = ConfigsProvider().load_rsi_clouds_settings()
        self.data = self.__prepare_data(data, _type)

    def __prepare_data(self, data: PriceDataFrame, _type: str) -> pd.DataFrame:
        match _type:
            case 'open/close' | 'Open/Close' | 'OPEN/CLOSE' | 'o/c' | 'O/C':
                return pd.DataFrame(data=((data.open + data.close) / 2).astype(np.float64), index=data.index)
            case 'high/low' | 'High/Low' | 'HIGH/LOW' | 'h/l' | 'H/L':
                return pd.DataFrame(data=((data.high + data.low) / 2).astype(np.float64), index=data.index)
            case 'open' | 'Open' | 'OPEN' | 'o' | 'O':
                return pd.DataFrame(data=data.open.astype(np.float64), index=data.index)
            case 'close' | 'Close' | 'CLOSE' | 'c' | 'C':
                return pd.DataFrame(data=data.close.astype(np.float64), index=data.index)
            case 'high' | 'High' | 'HIGH' | 'h' | 'H':
                return pd.DataFrame(data=data.high.astype(np.float64), index=data.index)
            case _:
                raise ValueError(f"Invalid _type value: {_type}")

    def calculate_rsi_macd(self) -> Any|None:
        self.rsi: pd.Series = ta.rsi(
            close=self.data,
            length=self.configs.rsi_period,
            scalar=self.configs.rsi_scalar,
            mamode=self.configs.rsi_mamode,
            talib=self.configs.rsi_talib_config,
            drift=self.configs.rsi_drift,
            offset=self.configs.rsi_drift
        )
        macd: pd.DataFrame = ta.macd(
            close=self.rsi,
            fast=self.configs.macd_fast,
            slow=self.configs.macd_slow,
            signal=self.configs.macd_signal,
            talib=self.configs.macd_talib_config,
            offset=self.configs.macd_offset
        )
        self.macd_line = macd[f'MACD_{self.configs.macd_fast}_{self.configs.macd_slow}_{self.configs.macd_signal}']
        self.macd_signal = macd[f'MACDs_{self.configs.macd_fast}_{self.configs.macd_slow}_{self.configs.macd_signal}']
        self.macd_histogram = macd[f'MACDh_{self.configs.macd_fast}_{self.configs.macd_slow}_{self.configs.macd_signal}']
        self.macd_cross_signal: pd.Series = pd.Series(
            np.where(
                (self.macd_line.shift(1) < self.macd_signal.shift(1)) & (self.macd_line > self.macd_signal),
                1,
                np.where(
                    (self.macd_line.shift(1) > self.macd_signal.shift(1)) & (self.macd_line < self.macd_signal),
                    -1,
                    0
                )
            )
        )
        self.histogram_cross_zero: pd.Series = pd.Series(
            np.where(
                (self.macd_histogram.shift(1) < 0) & (self.macd_histogram > 0),
                1,
                np.where(
                    (self.macd_histogram.shift(1) > 0) & (self.macd_histogram < 0),
                    -1,
                    0
                )
            )
        )
        return self.__get_last_macd_signal()

    def __get_last_macd_signal(self) -> Any|None:
        # Получение последнего сигнала пересечения MACD
        return None if self.macd_cross_signal.replace(0, np.nan).dropna().empty \
            else self.macd_cross_signal.replace(0, np.nan).dropna().iloc[-1]

    def create_visualization_rsi_macd(self) -> None:
        fig: plt.Figure
        axes: list[Axes]
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(10, 12))
        axes[0].plot(self.data.index, self.data, label='Цена')
        axes[0].set_title('Цена')
        axes[1].plot(self.data.index, self.rsi, label='RSI')
        axes[1].set_title('RSI')
        axes[2].plot(self.data.index, self.macd_line, label='MACD Line', color='blue')
        axes[2].plot(self.data.index, self.macd_signal, label='Signal Line', color='orange')
        axes[2].set_title('MACD')
        axes[3].bar(self.data.index, self.macd_histogram, label='MACD Histogram', color='purple')
        axes[3].set_title('MACD Histogram')
        axes[2].scatter(self.data.index, self.macd_cross_signal == 1, color='green', marker='^', label='Buy Signal')
        axes[2].scatter(self.data.index, self.macd_cross_signal == -1, color='red', marker='v', label='Sell Signal')
        axes[3].scatter(self.data.index, self.histogram_cross_zero != 0, color='black', marker='o', label='Zero Crossing')
        for ax in axes:
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Date')
        plt.tight_layout()
        plt.show()
