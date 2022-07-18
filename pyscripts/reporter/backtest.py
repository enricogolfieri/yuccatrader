import os
from this import d 
from freqtrade.data.btanalysis import load_backtest_data, load_backtest_stats
from tabulate import tabulate
import pandas as pd
from prettytable import PrettyTable
import reporter.project as pr 
import reporter.fileutils as fs


class Backtest:

    @staticmethod
    def strategy_comparison_fields():
        return ["key","trades","timeframe","timerange","timeframe_detail","profit_sum","profit_sum_pct","profit_total_abs","profit_total","profit_total_pct","duration_avg","wins","draws","losses","max_drawdown_account","max_drawdown_abs"]

    def __init__(self,pairs,test_name):
        self.__test_config = dict()
        self.__test_config['pairs'] = pairs
        self.__test_config['test_name'] = test_name

        table = { k:[] for k in Backtest.strategy_comparison_fields()}
        table["test_name"] = []
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
    @pr.exception("Backtest - Pretty Print")
    def pretty_print(self,path):
        with open(path, 'w+') as filewriter:        
            filewriter.write(tabulate(self.__df, tablefmt='psql'))
            pr.logger.info(f"Backtest - path {path}, saved")


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
    def add_strategy_result(self,result_dataframe): #dataframe
        table = { k: result_dataframe[k]for k in Backtest.strategy_comparison_fields() }

        #adding a colum with test name per strategy (this simplify the storage of information when gathering per strategy)
        test_name_list = [self.__test_config['test_name'] in result_dataframe["key"]]
        table["test_name"] = test_name_list

        df = pd.DataFrame(table)
        self.__df = pd.concat([self.__df ,df])



class BackTestCollection:
    def __init__(self):
        table = { k:[] for k in Backtest.strategy_comparison_fields()}
        table["test_name"] = []
        self.__df= pd.DataFrame(table)

    @pr.logdebug
    def append(self,backtest):
         self.__df = pd.concat([self.__df,backtest.dataframe()])


    @pr.logdebug
    def iterate_by_backtest(self):
        for data in self.__df.groupby("test_name").iterrows():
            return data 

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

    is_init = False
    backtest =Backtest("",test_name)
    nloaded = 0
    nfiles = 0
    for filename in os.listdir(path):
        if filename.endswith(".json") and not filename.endswith(".meta.json"):
            nfiles = nfiles + 1
            pr.logger.info(f"LOAD BACKTEST - path {path.joinpath(filename)}, loading")

            loaded_stats = load_backtest_stats(path.joinpath(filename))
            if 'strategy_comparison' in loaded_stats:
                nloaded = nloaded + 1
                if not is_init:
                    pairs = extract(loaded_stats,'pairlist')
                    test_name = os.path.splitext(filename)[0]
                    backtest = Backtest(pairs, test_name)
                    is_init = True
                stats = loaded_stats["strategy_comparison"][0]
                stats['timeframe']    = extract(loaded_stats,'timeframe')
                stats['timeframe_detail'] = extract(loaded_stats,'timeframe_detail')
                stats['timerange']    = extract(loaded_stats,'timerange') 
                backtest.add_strategy_result(stats)

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
