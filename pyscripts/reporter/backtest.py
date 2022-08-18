import os
from this import d 
from freqtrade.data.btanalysis import load_backtest_data, load_backtest_stats
from tabulate import tabulate
import pandas as pd
from prettytable import PrettyTable
import reporter.project as pr 
import reporter.fileutils as fs

@pr.logdebug
@pr.exception("Backtest - Pretty Print")
def pretty_print(df,path):
    with open(path, 'w+') as filewriter:        
        filewriter.write(tabulate(df, tablefmt='psql'))
        pr.logger.info(f"Backtest - path {path}, saved")


comparison_fields = ["key","trades","timeframe","timerange","market_change","timeframe_detail","profit_sum","profit_sum_pct","profit_total_abs","profit_total","profit_total_pct","duration_avg","wins","draws","losses","max_drawdown_account","max_drawdown_abs"]

def _filter_by_comparison_fields(dict):
    '''
    filter by dict
    '''
    return {k:dict[k] for k in comparison_fields}

def _initdf():
    '''
    init fields
    '''
    return {k:[] for k in comparison_fields}
 
_TEST_NAME="test_name"

class Backtest:

    def __init__(self):
        table = _initdf()
        table[_TEST_NAME] = []
        self.__df= pd.DataFrame(table)


    def iterate_by_strategy(self):
        '''
        iterate by strategy
        for data in backtest.iterate_by_strategy(self):
            ...
        '''
        for index, row in self.__df.iterrows():
            yield row


    def head(self,n):
        return self.__df.head(n)

    def sort(self,index):
        return self.__df.sort(index)

    @pr.logdebug
    def pretty_print(self,path):
        pretty_print(self.__df,path)


    @pr.logdebug
    @pr.exception("Backtest - save_as_csv")
    def save_as_csv(self,path):
        '''
        save backest as a csv  
        '''
        self.__df.to_csv(path)
        pr.logger.info(f"Backtest - Save as Csv - path {path}, saved")

        return    
    
    def dataframe(self):
        '''
        convert to pandas.DataFrame
        '''
        return self.__df

    @pr.logdebug
    def add_strategy_result(self,result_dataframe,test_name): #dataframe
        table = _filter_by_comparison_fields(result_dataframe)
        #adding a colum with test name per strategy (this simplify the storage of information when gathering per strategy)
        table[_TEST_NAME] = [test_name]
        df = pd.DataFrame(table)
        self.__df = pd.concat([self.__df ,df])


class BackTestCollection:
    def __init__(self):
        table = _initdf()
        table[_TEST_NAME] = []
        self.__df= pd.DataFrame(table)

    @pr.logdebug
    def append(self,backtest):
         self.__df = pd.concat([self.__df,backtest.dataframe()])


    @pr.logdebug
    def iterate_by_backtest(self):
        for name,data in self.__df.groupby(_TEST_NAME):
            yield data 

    @pr.logdebug
    def iterate_by_strategy(self):
        for name, dfgroup in self.__df.groupby("key"):
            yield dfgroup 



#load strategy
    
@pr.logdebug
def load_backtest(backtests_result_path,test_name):

    path = backtests_result_path.joinpath(test_name)

    def extract(stat,key):
        strategy_name = stat["strategy_comparison"][0]['key']
        return stat['strategy'][strategy_name][key]

    backtest =Backtest()
    nloaded = 0
    nfiles = 0
    for filename in os.listdir(path):
        if filename.endswith(".json") and not filename.endswith(".meta.json"):
            nfiles = nfiles + 1
            pr.logger.info(f"LOAD BACKTEST - path {path.joinpath(filename)}, loading")

            loaded_stats = load_backtest_stats(path.joinpath(filename))

            if 'strategy_comparison' in loaded_stats:
                nloaded = nloaded + 1

                stats = loaded_stats["strategy_comparison"][0]
                stats['timeframe']    = extract(loaded_stats,'timeframe')
                stats['timeframe_detail'] = extract(loaded_stats,'timeframe_detail')
                stats['timerange']    = extract(loaded_stats,'timerange') 
                stats['market_change'] = extract(loaded_stats,'market_change')
                backtest.add_strategy_result(stats,test_name)

    pr.logger.info(f"LOAD BACKTEST - path {path}, scraped files: {nfiles}, loaded {nloaded}")
    return backtest

@pr.logdebug
def load_backtest_collection(backtests_result_path):
    collection = BackTestCollection()
    for dir in os.listdir(backtests_result_path):
        backtest = load_backtest(backtests_result_path,dir)
        collection.append(backtest)
        pr.logger.info(f"LOAD BACKTEST COLLECTION - loaded backtest for test name {dir}")
    return collection 
