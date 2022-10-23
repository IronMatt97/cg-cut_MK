from matplotlib.cbook import report_memory
import solver
from docplex.mp.model import Model
from utils import MKPpopulate,  get_cut_stats
import os
import sys
import json



def solveCplex(instance) :
 # Call the function on a given instance
 c, A, b = MKPpopulate(instance)
 # Define the ranges for variables and constraints
 nCols, nRows = range(len(c)), range(len(b))
 # Get name
 txtname = instance.split("/")[1]
 name = txtname.split(".txt")[0]
 cplexlog = name+".log"
 # Create an empty model
 mkp = Model(name)
 mkp.set_log_output("solutions/"+cplexlog)
 # Define decision variables
 x = mkp.binary_var_list(nCols, lb = 0, ub = 1, name = 'x')
 constraints = mkp.add_constraints(sum(A[i][j] * x[j] for j in nCols) <= b[i] for i in nRows)
 profit = mkp.sum(c[j] * x[j] for j in nCols)
 mkp.add_kpi(profit, 'profit')
 objective = mkp.maximize(profit)
 # Tweak some CPLEX parameters so that CPLEX has a harder time to
 # solve the model and our cut separators can actually kick in.
 params = mkp.parameters
 params.threads = 1
 params.mip.strategy.heuristicfreq = -1
 params.mip.cuts.mircut = -1
 params.mip.cuts.implied = -1
 #params.mip.cuts.gomory = -1  ##ONLY GOMORY CUTS 
 params.mip.cuts.flowcovers = -1
 params.mip.cuts.pathcut = -1
 params.mip.cuts.liftproj = -1
 params.mip.cuts.zerohalfcut = -1
 params.mip.cuts.cliques = -1
 params.mip.cuts.covers = -1
 
 mkp.solve()
 # Reporting results
 cuts=get_cut_stats(mkp)
 print(f"-- cuts stats ", cuts)
 print(f"-- total #cuts = {sum(nk for _, nk in cuts.items())}")
 mkp.report()
 json_string= mkp.solution.export_as_json_string()
 file_path_json="solutions/"+name+".json"
 with open(file_path_json, "w") as output_file:
    json_ = json.dumps(json.loads(json_string), indent=4, sort_keys=True)
    output_file.write(json_)




if __name__ == '__main__':
    if len(sys.argv) == 1:
        for f in os.listdir("istances/") :
            print("solving "+f)
            solveCplex("istances/"+f)
    elif len(sys.argv) == 2:
        solveCplex(sys.argv[1])
    else:
        print("type  ::::python solver.py TESTNAME.txt::::")

