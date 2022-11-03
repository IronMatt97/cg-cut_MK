from internals.solver import solveInstance
from internals.general_utils import *
import pandas as pd
import warnings
import logging
import sys
import os

columns=["name", "cluster_type", "nvar","nconstraints","optimal_sol","sol","sol_is_integer","status","ncuts","elapsed_time","gap","relative_gap","iterations"]
logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # Flush Log
    flushLog("resolution.log")
    # Statistics variables in DataFrame
    stats = pd.DataFrame(columns=columns)
    # Read the configuration file
    config = ConfigParser()
    config.read('config.ini')

    if len(sys.argv) == 2:
        if not sys.argv[1]=="-all":
            invalidInput()
        else:
            print("Generating istances ....")
            for cluster in config.sections():
                generateIstances(cluster)
                print("Solving cluster '",cluster,"'...")
                for instance in os.listdir("instances/"+cluster+"/") :
                    stats=solveInstance(instance,cluster,stats)
                print("...Done.")

    elif len(sys.argv) == 3:
        execution_type = sys.argv[1]
        if execution_type == "-c":
            cluster=sys.argv[2]
            print("Generating istances ....")
            generateIstances(cluster)
            print("...Done.")
            
            print("Solving cluster '",cluster,"'...")
            for instance in os.listdir("instances/"+cluster+"/") :
                stats=solveInstance(instance,cluster,stats)
            print("...Done.")
            
        elif execution_type == "-s":
            stats=solveInstance(sys.argv[2].split("/")[2],sys.argv[2].split("/")[1],stats)
            print("...Done.")
        else:
            invalidInput()
    else:
        invalidInput()
    stats.to_excel("stats.xlsx")