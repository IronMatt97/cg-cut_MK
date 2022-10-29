from internals.solver import *
from internals.utils import *
import logging
import sys
import os
import pandas as pd


logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

if __name__ == '__main__':
    # Flush Log
    flushLog("resolution.log")
    # Generate istances 
    logging.info("Generating istances .... \n")
    generateIstances()
    logging.info(".....Done.")
    # Statistics variables in DataFrame
    columns=["name", "cluster_type", "nvar","nconstraints","optimal_sol","sol","sol_is_integer","status","ncuts","elapsed_time","gap"]
    stats = pd.DataFrame(columns=columns)
    if len(sys.argv) == 1:
        for cluster in os.listdir("instances/") :
            for instance in os.listdir("instances/"+cluster+"/") :
                logging.info("\n---------------------------------------------------")
                logging.info("Solving problem instance named "+instance+";\n")
                stats_i = solveProblem("instances/"+cluster+"/"+instance,cluster)
                stats=stats.append(pd.DataFrame(stats_i,columns=columns))      
                print("instance solved : \n,",instance)
        logging.info("---------------------------------------------------")
        stats.to_excel("stats.xlsx")
    elif len(sys.argv) == 2:
        cluster=sys.argv[1]
        logging.info("\n---------------------------------------------------")
        logging.info("Solving cluster :"+cluster)
        for instance in os.listdir("instances/"+cluster+"/") :
                logging.info("\n---------------------------------------------------")
                logging.info("Solving problem instance named "+instance+";\n")
                stats_i = solveProblem("instances/"+cluster+"/"+instance,cluster)
                print("instance solved : \n,",instance)
                stats=stats.append(pd.DataFrame(stats_i,columns=columns))      
        stats.to_excel("stats.xlsx")
        logging.info("---------------------------------------------------")
    else:
        logging.info("Invalid input.\nUsage:\n\t--> python solver.py\nor, in order to solve a specific cluster\n\t--> python solver.py {instace}.txt")

