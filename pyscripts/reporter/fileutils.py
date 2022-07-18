import os 
import reporter.project as pr  

def iterate_files(path):
    for filename in os.listdir(path):
        yield filename 

