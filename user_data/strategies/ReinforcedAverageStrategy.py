# --- Do not remove these libs ---
from email.policy import default
from freqtrade.strategy.interface import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame, merge, DatetimeIndex
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from technical.util import resample_to_interval, resampled_merge
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)
import freqtrade.vendor.qtpylib.indicators as qtpylib

class ReinforcedAverageStrategy(IStrategy):
    """

    author@: Gert Wohlgemuth

    idea:
        buys and sells on crossovers - doesn't really perfom that well and its just a proof of concept
    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.5
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.2

    # Optimal timeframe for the strategy
    timeframe = '4h'

    # trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = False

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # --- Define spaces for the indicators ---
    
    use_sell_signal_param = BooleanParameter(default=True)
    sell_profit_only_param = BooleanParameter(default=False)
    ignore_roi_if_buy_signal_param = BooleanParameter(default=False)

    maShort_period = IntParameter(2,30,default=8,space='buy')
    maMedium_period = IntParameter(2,80,default=14,space='buy')
    sma_period = IntParameter(25,100,default=50,space='buy')

    maShort_period_sell = IntParameter(2,30,default=8,space='sell')
    maMedium_period_sell = IntParameter(2,80,default=14,space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        self.use_sell_signal = self.use_sell_signal_param.value
        self.sell_profit_only = self.sell_profit_only_param.value
        self.ignore_roi_if_buy_signal = self.ignore_roi_if_buy_signal_param.value

        dataframe['maShort'] = ta.EMA(dataframe, timeperiod=self.maShort_period.value)
        dataframe['maMedium'] = ta.EMA(dataframe, timeperiod=self.maMedium_period.value)
        dataframe['maShortSell'] = ta.EMA(dataframe, timeperiod=self.maShort_period_sell.value)
        dataframe['maMediumSell'] = ta.EMA(dataframe, timeperiod=self.maMedium_period_sell.value)
        
        ##################################################################################
        # required for graphing
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_middleband'] = bollinger['mid']
        ##################################################################################
        self.resample_interval = timeframe_to_minutes(self.timeframe) * 12
        dataframe_long = resample_to_interval(dataframe, self.resample_interval)
        dataframe_long['sma'] = ta.SMA(dataframe_long, timeperiod=self.sma_period.value, price='close')
        dataframe = resampled_merge(dataframe, dataframe_long, fill_na=True)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """

        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe['maShort'], dataframe['maMedium']) &
                (dataframe['close'] > dataframe[f'resample_{self.resample_interval}_sma']) &
                (dataframe['volume'] > 0)
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
                qtpylib.crossed_above(dataframe['maMediumSell'], dataframe['maShortSell']) &
                (dataframe['volume'] > 0)
            ),
            'sell'] = 1
        return dataframe
