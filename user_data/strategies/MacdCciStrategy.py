
# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from pandas import DataFrame
# --------------------------------
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)

import talib.abstract as ta


class MacdCciStrategy(IStrategy):

    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.3

    # Optimal timeframe for the strategy
    timeframe = '5m'

    buy_cci = IntParameter(low=-700, high=0, default=-50, space='buy', optimize=True)
    sell_cci = IntParameter(low=0, high=700, default=100, space='sell', optimize=True)
    macd_fast_period = IntParameter(low=12, high=16, default=12, space='buy', optimize=True)
    macd_slow_period = IntParameter(low=20, high=30, default=26, space='buy', optimize=True)
    macd_signal_period = IntParameter(low=5, high=10, default=9, space='buy', optimize=True)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe, fastperiod=self.macd_fast_period.value, slowperiod=self.macd_slow_period.value, signalperiod=self.macd_signal_period.value)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['cci'] = ta.CCI(dataframe)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['cci'] <= self.buy_cci.value) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['macd'] < dataframe['macdsignal']) &
                (dataframe['cci'] >= self.sell_cci.value) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 1

        return dataframe
