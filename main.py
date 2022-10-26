import main
import sys
import os
from internals.solver import *
from internals.utils import *

if __name__ == '__main__':
    if len(sys.argv) == 1:
        for file in os.listdir("istances/") :
            print("\n---------------------------------------------------")
            print("Solving problem instance named "+file+";\n")
            solveCplex("istances/"+file)
            #SolveProb()
        print("---------------------------------------------------")
    elif len(sys.argv) == 2:
        print("\n---------------------------------------------------")
        print("Solving problem instance named "+sys.argv[1])
        solveCplex(sys.argv[1])
        print("---------------------------------------------------")
    else:
        print("Invalid input.\nUsage:\n\t--> python solver.py\nor, in order to solve a specific instance\n\t--> python solver.py {instace}.txt")

