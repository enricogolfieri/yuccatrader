import argparse
from cgi import test
import csv
from turtle import back
import reporter.project as pr

parser = argparse.ArgumentParser(description='Scan /backtest_result and write a report in backtest_repoorts ')
parser.add_argument('-n','--name', help='Test name', required=True)
parser.add_argument('-o','--official', help='save reports into official folder instead of tmp folder', required=False)

parser.add_argument('--nolog', action='store_true', help='Disable logging', required=False)

import os 
from reporter.backtest import Backtest,load_backtest,load_backtest_collection

print("##################################################################### ")
args = vars(parser.parse_args())
pr.init_log(not args['nolog'])

pr.logger.info(f"csv_report started with args: {args}")

test_name = args['name']
is_official=args['official']

    
pr.logger.info(f"CSV-REPORT: start report for test {test_name}")

backtest = load_backtest(pr.backtest_results(),test_name)

if backtest is None:
    pr.logger.error(f"Error - loaded backtest is None, path {pr.backtest_results(test_name)}")

else:
    backtest.save_as_csv(pr.backtest_reports(test_name,"report.csv",official=is_official))
    backtest.pretty_print(pr.backtest_reports(test_name,"report.txt",official=is_official))

pr.logger.info("CSV-REPORT: start summary of strategy")

backtest_collection = load_backtest_collection(pr.backtest_results())

for dfstrategy in backtest_collection.iterate_by_strategy():
    print(dfstrategy)
    csv_name = f"{dfstrategy.iloc[0]['key']}.csv"
    path = pr.backtest_reports("summary",csv_name,official=is_official)
    dfstrategy.to_csv(path)
    pr.logger.info(f"Summary of strategy - save csv file - path {path}, saved")
