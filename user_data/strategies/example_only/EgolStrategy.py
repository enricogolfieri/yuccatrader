# Hour Strategy
# In this strategy we try to find the best hours to buy and sell in a day.(in hourly timeframe)
# Because of that you should just use 1h timeframe on this strategy.
# Author: @Mablue (Masoud Azizi)
# github: https://github.com/mablue/
# Requires hyperopt before running.
# freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --strategy HourBasedStrategy -e 200


import numpy
from freqtrade.strategy import IntParameter, IStrategy
from pandas import DataFrame
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta

# --------------------------------
# Add your lib to import here
# No need to These imports. just for who want to add more conditions:
# import talib.abstract as ta
# import freqtrade.vendor.qtpylib.indicators as qtpylib

def vote(results,w):
    a = numpy.zeros(len(results))
    a[:] =-1*w
    a[results] = w
    return a

class CrossStrategy(object):

    def __init__(self,weight_buy,weight_sell) -> None:
        self.weight_buy = weight_buy
        self.weight_sell = weight_sell
    
    def buy(self,dataframe,short_index,long_index):
        results = qtpylib.crossed_above(dataframe[short_index], dataframe[long_index])
        return vote(results,self.weight_buy)

    def sell(self,dataframe,short_index,long_index):
        results = qtpylib.crossed_above(dataframe[short_index], dataframe[long_index])
        return vote(results,self.weight_sell)
class CrossEma(object):

    def __init__(self,strategy):
        self.__strategy = strategy
        self.__cross_strategy = CrossStrategy(self.__strategy.ema_weight_buy.value,self.__strategy.ema_weight_sell.value)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=self.__strategy.ema_short_period.value)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod= self.__strategy.ema_long_period.value)
        dataframe['ema_short_sell'] = ta.EMA(dataframe, timeperiod=self.__strategy.ema_short_sell_period.value)
        dataframe['ema_long_sell'] = ta.EMA(dataframe, timeperiod=self.__strategy.ema_long_sell_period.value)

    def buy(self,dataframe,metadata) -> int:
        return self.__cross_strategy.buy(dataframe,'ema_short','ema_long')
 

    def sell(self,dataframe,metadat) -> int:
        return self.__cross_strategy.sell(dataframe,'ema_short_sell','ema_long_sell')

class CrossMa(object):
    
        def __init__(self,strategy):
            self.__strategy = strategy
            self.__cross_strategy = CrossStrategy(self.__strategy.ma_weight_buy.value,self.__strategy.ma_weight_sell.value)
    
        def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
            dataframe['ma_short'] = ta.MA(dataframe, timeperiod=self.__strategy.ma_short_period.value)
            dataframe['ma_long'] = ta.MA(dataframe, timeperiod= self.__strategy.ma_long_period.value)
            dataframe['ma_short_sell'] = ta.MA(dataframe, timeperiod=self.__strategy.ma_short_sell_period.value)
            dataframe['ma_long_sell'] = ta.MA(dataframe, timeperiod=self.__strategy.ma_long_sell_period.value)
    
        def buy(self,dataframe,_) -> int:
            return self.__cross_strategy.buy(dataframe,'ma_short','ma_long')
    
    
        def sell(self,dataframe,_) -> int:
            return self.__cross_strategy.sell(dataframe,'ma_short_sell','ma_long_sell')

class CrossDema(object):
        
        def __init__(self,strategy):
            self.__strategy = strategy
            self.__cross_strategy = CrossStrategy(self.__strategy.dema_weight_buy.value,self.__strategy.dema_weight_sell.value)
    
        def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
            dataframe['dema_short'] = ta.DEMA(dataframe, timeperiod=self.__strategy.dema_short_period.value)
            dataframe['dema_long'] = ta.DEMA(dataframe, timeperiod= self.__strategy.dema_long_period.value)
            dataframe['dema_short_sell'] = ta.DEMA(dataframe, timeperiod=self.__strategy.dema_short_sell_period.value)
            dataframe['dema_long_sell'] = ta.DEMA(dataframe, timeperiod=self.__strategy.dema_long_sell_period.value)
    
        def buy(self,dataframe,_) -> int:
            return self.__cross_strategy.buy(dataframe,'dema_short','dema_long')
    
    
        def sell(self,dataframe,_) -> int:
            return self.__cross_strategy.sell(dataframe,'dema_short_sell','dema_long_sell')


class RsiStrategy(object):
    
    def __init__(self,strategy):
        self.__strategy = strategy

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.__strategy.rsi_period.value)
        dataframe['rsi_sell'] = ta.RSI(dataframe, timeperiod=self.__strategy.rsi_sell_period.value)

    def buy(self,dataframe,_) -> int:
        results = dataframe['rsi'].between(20, 40)
        return vote(results,self.__strategy.rsi_weight_buy.value)

    def sell(self,dataframe,_) -> int:
        results = dataframe['rsi_sell'].between(20, 40)
        return vote(results,self.__strategy.rsi_weight_sell.value)

class MACD(object):

    def __init__(self,strategy):
        self.__strategy = strategy

    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['cci'] = ta.CCI(dataframe)

        return dataframe

    def buy(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        a = numpy.array(dataframe['macd'] < dataframe['macdsignal'])
        b = numpy.array(dataframe['cci'] <= self.__strategy.macd_buy_cci.value)
        c = numpy.array(dataframe['volume'] > 0 ) # Make sure Volume is not 0]
        results = a & b & c

        return vote(results,self.__strategy.macd_weight_buy.value)

    def sell(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        a = numpy.array(dataframe['macd'] < dataframe['macdsignal'])
        b = numpy.array(dataframe['cci'] >= self.__strategy.macd_sell_cci.value)
        c = numpy.array(dataframe['volume'] > 0 ) # Make sure Volume is not 0]
        results = a & b & c

        return vote(results,self.__strategy.macd_weight_sell.value)
class MomentumStrategy(object):
        # --- Define spaces for the indicators ---

    def __init__(self, buy_adx, sell_adx, adx_timeperiod,buy_mom,sell_mom,mom_timeperiod,buy_plus_di,sell_minus_di,plus_di_timeperiod,minus_di_timeperiod,momentum_buy_weight,momentum_sell_weight) -> None:
        self.adx_timeperiod = adx_timeperiod
        self.plus_di_timeperiod = plus_di_timeperiod
        self.minus_di_timeperiod = minus_di_timeperiod
        self.mom_timeperiod = mom_timeperiod
        self.buy_adx = buy_adx
        self.sell_adx = sell_adx
        self.buy_plus_di = buy_plus_di
        self.sell_minus_di = sell_minus_di
        self.buy_mom = buy_mom
        self.sell_mom = sell_mom
        self.momentum_sell_weight = momentum_sell_weight
        self.momentum_buy_weight = momentum_buy_weight

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_timeperiod.value)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe, timeperiod=self.plus_di_timeperiod.value)
        dataframe['minus_di'] = ta.MINUS_DI(dataframe, timeperiod=self.minus_di_timeperiod.value)
        dataframe['mom'] = ta.MOM(dataframe, timeperiod=self.mom_timeperiod.value)

        return dataframe

    def buy(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        result = ( (dataframe['adx'] > self.buy_adx.value) &
            (dataframe['mom'] > self.buy_mom.value) &
            (dataframe['plus_di'] > self.buy_plus_di.value) &
            (dataframe['plus_di'] > dataframe['minus_di']))

        return vote(result,self.momentum_buy_weight.value)


    def sell(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        result = ( (dataframe['adx'] > self.sell_adx.value) &
            (dataframe['mom'] < self.sell_mom.value) &
            (dataframe['minus_di'] > self.sell_minus_di.value) &
            (dataframe['plus_di'] < dataframe['minus_di']))
        
        return vote(result,self.momentum_sell_weight.value)

class EgolStrategy(IStrategy):

    # ROI table:
    minimal_roi = {
        "0": 0.1
    }

    # Stoploss:
    stoploss = -0.10

    # CrossEma:
    ema_short_period = IntParameter(2,15,default=8,space='buy')
    ema_long_period = IntParameter(15,50,default=14,space='buy')

    ema_short_sell_period = IntParameter(2,15,default=8,space='sell')
    ema_long_sell_period= IntParameter(15,50,default=14,space='sell')

    ema_weight_buy = IntParameter(0, 10, default=1, space='buy')
    ema_weight_sell = IntParameter(0, 10, default=1, space='sell')


    #CrossMa
    ma_short_period = IntParameter(2,15,default=8,space='buy')
    ma_long_period = IntParameter(15,50,default=14,space='buy')

    ma_short_sell_period = IntParameter(2,15,default=8,space='sell')
    ma_long_sell_period= IntParameter(15,50,default=14,space='sell')

    ma_weight_buy = IntParameter(0, 10, default=1, space='buy')
    ma_weight_sell = IntParameter(0, 10, default=1, space='sell')

    #CrossDema
    dema_short_period = IntParameter(2,15,default=8,space='buy')
    dema_long_period = IntParameter(15,50,default=14,space='buy')

    dema_short_sell_period = IntParameter(2,15,default=8,space='sell')
    dema_long_sell_period = IntParameter(15,50,default=14,space='sell')

    dema_weight_buy = IntParameter(0, 10, default=1, space='buy')
    dema_weight_sell = IntParameter(0, 10, default=1, space='sell')


    # MomentumStrategy:

    buy_adx = IntParameter(15, 35, default=25, space="buy")
    sell_adx = IntParameter(15, 35, default=25, space="sell")
    adx_timeperiod = IntParameter(7, 21, default=14, space="buy")
    
    buy_mom = IntParameter(-5, 5, default=0, space="buy")
    sell_mom = IntParameter(-5, 5, default=0, space="sell")
    mom_timeperiod = IntParameter(20, 30, default=25, space="buy")

    buy_plus_di = IntParameter(15, 35, default=25, space="buy")
    sell_minus_di = IntParameter(15, 35, default=25, space="sell")
    plus_di_timeperiod = IntParameter(20, 30, default=25, space="buy")
    minus_di_timeperiod = IntParameter(20, 30, default=25, space="buy")

    momentum_buy_weight = IntParameter(0, 10, default=1, space="buy")
    momentum_sell_weight = IntParameter(0, 10, default=1, space="sell")

    #RsiStrategy:
    rsi_period = IntParameter(10, 30, default=15, space='buy')
    rsi_sell_period = IntParameter(70, 90, default=75, space='sell')

    rsi_weight_buy = IntParameter(0, 10, default=1, space='buy')
    rsi_weight_sell = IntParameter(0, 10, default=1, space='sell')

    #MacdStrategy:

    macd_buy_cci = IntParameter(low=-700, high=0, default=-50, space='buy', optimize=True)
    macd_sell_cci = IntParameter(low=0, high=700, default=100, space='sell', optimize=True)
    macd_weight_buy = IntParameter(0, 10, default=1, space='buy')
    macd_weight_sell = IntParameter(0, 10, default=1, space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #crossEma = CrossEma(self)
        #crossMa = CrossMa(self)
        crossDema = CrossDema(self)
        macd = MACD(self)
        momentum = MomentumStrategy(self.buy_adx,self.sell_adx,self.adx_timeperiod,self.buy_mom,self.sell_mom,self.mom_timeperiod,self.buy_plus_di,self.sell_minus_di,self.plus_di_timeperiod,self.minus_di_timeperiod,self.momentum_buy_weight,self.momentum_sell_weight)
        rsi = RsiStrategy(self)

        self.strategies = [crossDema,macd,momentum,rsi]

        for strategy in self.strategies:
            strategy.populate_indicators(dataframe, metadata)

        return  dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        tuple_results = tuple((strategy.buy(dataframe,metadata),) for strategy in self.strategies)
        numpy_results = numpy.concatenate( tuple_results)
        results = numpy_results.sum(axis=0) > 0

        dataframe.loc[ results > 0, 'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        tuple_results = tuple((strategy.sell(dataframe,metadata),) for strategy in self.strategies)
        numpy_results = numpy.concatenate( tuple_results)
        results = numpy_results.sum(axis=0) > 0

        dataframe.loc[ results > 0, 'sell'] = 1

        return dataframe
