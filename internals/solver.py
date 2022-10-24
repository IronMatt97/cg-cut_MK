from utils import MKPpopulate, get_cut_stats
from matplotlib.cbook import report_memory
from docplex.mp.model import Model
import solver
import json
import sys
import os


# This function solves a specific problem instance
def solveCplex(instance) :
    # Retrieve the matrixes of the problem instance
    c, A, b = MKPpopulate(instance) 
    nCols, nRows = range(len(c)), range(len(b))
    # Get the instance name
    txtname = instance.split("/")[1]    
    name = txtname.split(".txt")[0]
    cplexlog = name+".log"
    # Create an empty model
    mkp = Model(name)
    mkp.set_log_output("solutions/"+cplexlog)
    # Define the decision variables
    x = mkp.binary_var_list(nCols, lb = 0, ub = 1, name = 'x')
    constraints = mkp.add_constraints(sum(A[i][j] * x[j] for j in nCols) <= b[i] for i in nRows)
    profit = mkp.sum(c[j] * x[j] for j in nCols)
    mkp.add_kpi(profit, 'profit')
    objective = mkp.maximize(profit)
    # Parameters Tweak 
    params = mkp.parameters
    params.threads = 1
    params.mip.strategy.heuristicfreq = -1
    params.mip.cuts.mircut = -1
    params.mip.cuts.implied = -1
    #params.mip.cuts.gomory = -1  # We only want Gomory cuts to be done 
    params.mip.cuts.flowcovers = -1
    params.mip.cuts.pathcut = -1
    params.mip.cuts.liftproj = -1
    params.mip.cuts.zerohalfcut = -1
    params.mip.cuts.cliques = -1
    params.mip.cuts.covers = -1
 
    # Resolve the problem instance
    mkp.solve()
    # Report the results
    cuts=get_cut_stats(mkp)
    print("\n\t-Cuts stats:\n\t", cuts)
    print("\n\t-Total number of cuts = {0}\n".format(sum(nk for _, nk in cuts.items())))
    print("FINAL REPORT:")
    mkp.report()
    json_string= mkp.solution.export_as_json_string()
    file_path_json="solutions/"+name+".json"
    with open(file_path_json, "w") as output_file:
        json_ = json.dumps(json.loads(json_string), indent=4, sort_keys=True)
        output_file.write(json_)




if __name__ == '__main__':
    if len(sys.argv) == 1:
        for file in os.listdir("istances/") :
            print("\n---------------------------------------------------")
            print("Solving problem instance named "+file+";\n")
            solveCplex("istances/"+file)
        print("---------------------------------------------------")
    elif len(sys.argv) == 2:
        print("\n---------------------------------------------------")
        print("Solving problem instance named "+sys.argv[1])
        solveCplex(sys.argv[1])
        print("---------------------------------------------------")
    else:
        print("Invalid input.\nUsage:\n\t--> python solver.py\nor, in order to solve a specific instance\n\t--> python solver.py {instace}.txt")

