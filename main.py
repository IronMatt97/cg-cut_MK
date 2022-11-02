from internals.solver import *
from internals.utils import *
import warnings
import logging
import sys
import os
import pandas as pd

# TODO applicare i tagli iterativamente e loggare iterativamente su excel

logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')
columns=["name", "cluster_type", "nvar","nconstraints","optimal_sol","sol","sol_is_integer","status","ncuts","elapsed_time","gap","iterations","low","upper"]
warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == '__main__':
    # Flush Log
    flushLog("resolution.log")
   
    # Statistics variables in DataFrame
    stats = pd.DataFrame(columns=columns)
    if len(sys.argv) == 1:
        logging.info("\n---------------------------------------------------")
        for cluster in os.listdir("instances/") :
            # Generate istances 
            print("Generating istances .... \n")
            generateIstances(cluster)
            print("...Done.")
            print("Solving cluster '",cluster,"'...")
            for instance in os.listdir("instances/"+cluster+"/") :
                logging.info("\n---------------------------------------------------")
                logging.info("Solving problem instance '"+instance+"';\n")
                stats_i = solveProblem("instances/"+cluster+"/"+instance,cluster)
                stats=stats.append(pd.DataFrame(stats_i,columns=columns))
            print("...Done.")
        logging.info("---------------------------------------------------")
    elif len(sys.argv) == 2:
        cluster=sys.argv[1]
        # Generate istances 
        print("Generating istances .... \n")
        generateIstances(cluster)
        print("...Done.")
        logging.info("\n---------------------------------------------------")
        print("Solving cluster '",cluster,"'...")
        for instance in os.listdir("instances/"+cluster+"/") :
            logging.info("\n---------------------------------------------------")
            logging.info("Solving problem instance '"+instance+"';\n")
            stats_i = solveProblem("instances/"+cluster+"/"+instance,cluster)
            stats=stats.append(pd.DataFrame(stats_i,columns=columns))
        print("...Done.")
        logging.info("---------------------------------------------------")
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-s":
            print("Solving single instance named '"+sys.argv[2]+"'")
            stats_i = solveProblem("instances/"+"cluster_small/"+sys.argv[2],"cluster_small")
            stats=stats.append(pd.DataFrame(stats_i,columns=columns))
        print("...Done.")
    else:
        logging.info("Invalid input.\nUsage:\n\t--> python solver.py\nor, in order to solve a specific cluster\n\t--> python solver.py {cluster}.txt")
    stats.to_excel("stats.xlsx")

