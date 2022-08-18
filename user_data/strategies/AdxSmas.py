# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)


# --------------------------------


class AdxSmas(IStrategy):
    """

    author@: Gert Wohlgemuth

    converted from:

    https://github.com/sthewissen/Mynt/blob/master/src/Mynt.Core/Strategies/AdxSmas.cs

    """

    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.1
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.25

    # Optimal timeframe for the strategy
    timeframe = '1h'


    buy_adx = IntParameter(20, 75, default=25, space="buy")
    sell_adx = IntParameter(10, 35, default=25, space="sell")
    adx_timeperiod = IntParameter(7, 21, default=14, space="buy")
    
    sma_short_timeperiod = IntParameter(2, 20, default=3, space="buy")
    sma_long_timeperiod = IntParameter(20, 80, default=25, space="buy")


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_timeperiod.value)
        dataframe['short'] = ta.SMA(dataframe, timeperiod=self.sma_short_timeperiod.value)
        dataframe['long'] = ta.SMA(dataframe, timeperiod=self.sma_long_timeperiod.value)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] > self.buy_adx.value) &
                    (qtpylib.crossed_above(dataframe['short'], dataframe['long']))

            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] < self.sell_adx.value) &
                    (qtpylib.crossed_above(dataframe['long'], dataframe['short']))

            ),
            'sell'] = 1
        return dataframe
