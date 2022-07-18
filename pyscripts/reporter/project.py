import os 
import pathlib

import logging
import logging.handlers
import os
 
from datetime import datetime
from re import sub

__curr_dir=pathlib.Path(__file__).parent.resolve()


def root(sub=None):
    if sub:
        return __curr_dir.parent.parent.joinpath(sub).resolve()
    else:
        return __curr_dir.parent.parent.resolve()

def userdata(sub=None):
    if sub:
        return root('user_data').joinpath(sub).resolve()
    else:
        return root('user_data').resolve()

def pyscripts(subdir = None):
    if subdir:
        return root('pyscripts').joinpath(subdir).resolve()
    else:
        return root('pyscripts').resolve()

def __compose_sub_userdata(mainfolder,subfolder=None,filename = None):
    
    if subfolder:
        path = userdata(mainfolder).joinpath(subfolder).resolve()
    else:
        path =  userdata(mainfolder).resolve()      
    if not os.path.exists(path):
        os.mkdir(path)

    if filename:
        print(f"about to save {path.joinpath(filename).resolve()}")
        return path.joinpath(filename).resolve()
    else:
        return path

def backtest_results(subdir=None,filename = None):
    return __compose_sub_userdata("backtest_results",subdir,filename)

def backtest_reports(subdir=None,filename = None, official = False):
    if official:
        return __compose_sub_userdata("backtest_reports",subdir,filename)
    else:
        return __compose_sub_userdata("backtest_tmp_reports",subdir,filename)

logger = logging.getLogger('reporter-logger')

def init_log(enable):
    global logger
    if enable:
        #init logging
        logfile =  "csv_report.log"

        handler = logging.handlers.WatchedFileHandler(
        os.environ.get("LOGFILE", pyscripts('logs').joinpath(logfile)), mode='w')

        formatter = logging.Formatter(logging.BASIC_FORMAT)

        handler.setFormatter(formatter)
        
        logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        logger.addHandler(handler)
        logger.disabled = False
        logger.info(f"log enabled {enable}")
    else:
        logger.disabled = True 


import functools

def logdebug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        logger.info(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        logger.info(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug

def exception(log_id):
    def inner(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args,**kwargs)
            except Exception as e:
                logger.error(f"{log_id} - exception {e}")
        return wrapper
    return inner 