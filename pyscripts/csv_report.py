import argparse
from reporter.backtest import pretty_print
import reporter.project as paths

parser = argparse.ArgumentParser(description='Scan /backtest_result and write a report in backtest_repoorts ')
parser.add_argument('-o','--official', help='save reports into official folder instead of tmp folder', required=False)

parser.add_argument('--nolog', action='store_true', help='Disable logging', required=False)

import os 
from reporter.backtest import Backtest,load_backtest,load_backtest_collection

print("##################################################################### ")
args = vars(parser.parse_args())
paths.init_log(not args['nolog'])

paths.logger.info(f"csv_report started with args: {args}")

is_official=args['official']


paths.logger.info("CSV-REPORT: start summary of strategy")

backtest_collection = load_backtest_collection(paths.backtest_results())

for dfstrategy in backtest_collection.iterate_by_strategy():
    print(dfstrategy)
    csv_name = f"{dfstrategy.iloc[0]['key']}.csv"
    path = paths.backtest_reports("summary",csv_name,official=is_official)
    dfstrategy.to_csv(path)
    paths.logger.info(f"Summary of strategy - save csv file - path {path}, saved")

paths.logger.info(f"CSV-REPORT: start report generation")

for dftest in backtest_collection.iterate_by_backtest():
    print( "##################################################################### ")
    print(dftest)
    test_name = dftest.iloc[0]['key']

    dftest.to_csv(paths.backtest_reports(test_name,"report.csv",official=is_official))
    pretty_print(dftest,paths.backtest_reports(test_name,"report.txt",official=is_official))

    paths.logger.info(f"Backtest- save report csv file - path {path}, saved")