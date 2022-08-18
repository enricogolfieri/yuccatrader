# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)


# --------------------------------


class BbandRsi(IStrategy):
    """

    author@: Gert Wohlgemuth

    converted from:

    https://github.com/sthewissen/Mynt/blob/master/src/Mynt.Core/Strategies/BbandRsi.cs

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

    buy_rsi = IntParameter(25, 35, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    rsi_period = IntParameter(7, 21, default=14, space="buy")

    bbwindow = IntParameter(low=8, high=20, default=12, space='buy', optimize=True)
    bbdeviation = DecimalParameter(low=1, high=3, default=2,  decimals = 2, space='buy', optimize=True) 
    bbscalar_buy = DecimalParameter(low=0.95, high=1.05, decimals = 2, default=1, space='buy', optimize=True)
    bbscalar_sell = DecimalParameter(low=0.95, high=1.05, decimals = 2, default=1, space='sell', optimize=True)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.buy_rsi.value)

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=self.bbwindow.value, stds=self.bbdeviation.value)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] < self.buy_rsi.value) &
                    (dataframe['close'] < self.bbscalar_buy.value * dataframe['bb_lowerband'])

            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] > self.sell_rsi.value) &
                    (dataframe['close'] > self.bbscalar_sell.value * dataframe['bb_upperband'])
            ),
            'sell'] = 1
        return dataframe
