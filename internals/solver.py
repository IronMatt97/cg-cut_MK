from pprint import pprint
from internals.utils import MKPpopulate, get_cut_stats
from matplotlib.cbook import report_memory
import cplex 
import json
import string


# This function solves a specific problem instance
def solveCplex(instance) :
    # Retrieve the matrixes of the problem instance
    c, A, b = MKPpopulate(instance) 
    #print(c,"\n\n",A,"\n\n",b,"\n\n")
    #print(A[0][1])
    nCols, nRows =(len(c)), (len(b))
    
    # Get the instance name
    txtname = instance.split("/")[1]    
    name = txtname.split(".txt")[0]
    cplexlog = name+".log"
    path_log = str("solutions/"+cplexlog)

    # -------------------------

    names = []
    lower_bounds = []
    upper_bounds = []
    types=[]
    constraint_names = []
    constraint_senses = []

    for i in range(nCols):
        names.append("x"+str(i))
        lower_bounds.append(0.0)
        upper_bounds.append(1.0)
        types.append("C")

    for i in range(nRows):
        constraint_names.append("c"+str(i))
        constraint_senses.append("L")

    print("names ",names)
    print("lower_bounds ",lower_bounds)
    print("upper_bounds ",upper_bounds)
    print("types", types)
    print("constraint_senses ", constraint_senses)
    print("constraint names ", constraint_names)
    #--------------------------------------------------------
    with cplex.Cplex() as my_problem:

        my_problem.set_problem_name(name)
        my_problem.set_problem_name(name)
        my_problem.objective.set_sense(my_problem.objective.sense.maximize)

        # Parameters Tweak 
        params = my_problem.parameters
        params.workmem.set(8192)
        # Disable presolve 
        params.preprocessing.presolve = 0 
        params.mip.strategy.heuristicfreq = -1
        params.mip.cuts.mircut = -1
        params.mip.cuts.implied = -1
        params.mip.cuts.gomory = -1  
        params.mip.cuts.flowcovers = -1
        params.mip.cuts.pathcut = -1
        params.mip.cuts.liftproj = -1
        params.mip.cuts.zerohalfcut = -1
        params.mip.cuts.cliques = -1
        params.mip.cuts.covers = -1
            
        # Add variables --------------------------------------------------------------------
        print("\n ------ \n")
        print("ADD VARIABLES")

        num_decision_var = nCols
        print("NUM DECISION VAR", num_decision_var)

        my_problem.variables.add(names= ["x"+str(i) for i in range(num_decision_var)])
        print("variables added\n")
    
        for i in range(nCols):
            my_problem.variables.set_lower_bounds(i, lower_bounds[i])
            my_problem.variables.set_upper_bounds(i, upper_bounds[i])
            my_problem.variables.set_types(names[i], my_problem.variables.type.continuous)

        print("\n ------ \n")


        print("set variables " ,my_problem.variables.get_names())
        # Add contraint ----------------------------------------------------------


        for i in range(nRows):
            my_problem.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])],
            rhs= [b[i]],
            names = [constraint_names[i]],
            senses = [constraint_senses[i]]
        )
        print("set constraints done\n")
        
        # Objective ---------------------------------------
        objective = c
        print("set objective ",objective)
        assert(len(objective)==len(lower_bounds))
        assert(len(objective)==len(upper_bounds))
        assert(len(objective)==len(names))
        print("---")
        
        
        for i in range(nCols): 
            my_problem.objective.set_linear([(i, c[i])])
    
        # Resolve the problem instance
        my_problem.solve()
        # Report the results
        #cuts=get_cut_stats(mkp)
        #print("\n\t-Cuts stats:\n\t", cuts)
        #print("\n\t-Total number of cuts = {0}\n".format(sum(nk for _, nk in cuts.items())))
        if not my_problem.solution.get_objective_value().is_integer() : 
            iterateGomory(my_problem)
        
        print("FINAL REPORT:")
        print(my_problem.solution.get_values())
        my_problem.write("lp/"+name+".lp")
        my_problem.solution.write(path_log)
        
        my_problem.end()
        pass




    

def iterateGomory(mkp) : 
    print("UP : ",mkp.solution.get_objective_value())
    iter = 0 
    #binvcol = mkp.solution.advanced.binvcol()
   # binvrow = mkp.solution.advanced.binvrow()
   # binvacol = mkp.solution.advanced.binvacol()
   # binvarow = mkp.solution.advanced.binvarow()


