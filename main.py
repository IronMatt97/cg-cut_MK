from internals.solver import *
from internals.utils import *
import logging
import sys
import os

logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

if __name__ == '__main__':
    flushLog("resolution.log")
    if len(sys.argv) == 1:
        for file in os.listdir("instances/") :
            logging.info("\n---------------------------------------------------")
            logging.info("Solving problem instance named "+file+";\n")
            solveProblem("instances/"+file)
        logging.info("---------------------------------------------------")
    elif len(sys.argv) == 2:
        fileName=sys.argv[1]
        logging.info("\n---------------------------------------------------")
        logging.info("Solving problem instance named "+fileName)
        solveProblem(fileName)
        logging.info("---------------------------------------------------")
    else:
        logging.info("Invalid input.\nUsage:\n\t--> python solver.py\nor, in order to solve a specific instance\n\t--> python solver.py {instace}.txt")

