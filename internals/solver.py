from numpy import outer
from internals.utils import *
from time import *
from cplex.callbacks import MIPInfoCallback
import cplex
import matplotlib.pyplot as plt
import os
import logging

logging.basicConfig(filename='log.txt', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

class TimeLimitCallback(MIPInfoCallback):
    def __call__(self):
        if not self.aborted and self.has_incumbent():
            gap = 100.0 * self.get_MIP_relative_gap()
            timeused = self.get_time() - self.starttime
            if timeused > self.timelimit:
                logging.info("Good enough solution at", timeused, "sec., gap =",
                      gap, "%, quitting.")
                self.aborted = True
                self.abort()

# This function solves a specific problem instance
def solveCplex(instance) :
    # Retrieve the matrixes of the problem instance
    c, A, b = MKPpopulate(instance) 
    nCols, nRows =(len(c)), (len(b))
    
    # Get the instance name
    txtname = instance.split("/")[1]    
    name = txtname.split(".txt")[0]
    if not os.path.exists("solutions/"+name):
            os.makedirs("solutions/"+name)
    if not os.path.exists("lp/"+name):
            os.makedirs("lp/"+name)
   
    path_base_log = str("solutions/"+name)
    path_base_lp = str("lp/"+name)

    #Program variables section ####################################################

    names = []
    all_constraints = []
    lower_bounds = []
    upper_bounds = []
    constraint_names = []
    constraint_senses = []

    for i in range(nCols):
        names.append("x"+str(i))
        lower_bounds.append(0.0)
        upper_bounds.append(1.0)

    for i in range(nRows):
        constraint_names.append("c"+str(i))
        constraint_senses.append("L")

    logging.info("...Checking input coherency")
    assert(len(c)==len(lower_bounds))
    assert(len(c)==len(upper_bounds))
    assert(len(c)==len(names))
    logging.info("... Done.")
    
    # Solver section    ############################################################

    #First of all determine the optimal solution
    optimal_value,vars = determineOptimal(instance)
    logging.info("OPTIMAL PLI SOLUTION IS %f",optimal_value)
    logging.info("Variables: %s",vars)

    with cplex.Cplex() as mkp,  open("cplex_log.txt", "w") as f:
        mkp.set_problem_name(name)
        mkp.objective.set_sense(mkp.objective.sense.maximize)
        mkp.set_log_stream(f)
        mkp.set_error_stream(f)
        mkp.set_warning_stream(f)
        mkp.set_results_stream(f)
        params = mkp.parameters
        # Disable presolve 
        params.preprocessing.presolve.set(0) 
        # Register Callback 
        timelim_cb = mkp.register_callback(TimeLimitCallback)
        # Set time limit
        timelim_cb.timelimit = 60*3  #3 min max
        timelim_cb.aborted = False
        # Add variables --------------------------------------------------------------------
        mkp.variables.add(names= ["x"+str(i) for i in range(nCols)])
    
        for i in range(nCols):
            mkp.variables.set_lower_bounds(i, lower_bounds[i])
            mkp.variables.set_upper_bounds(i, upper_bounds[i])

        # Add contraints -------------------------------------------------------------------
        for i in range(nRows):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])], rhs= [b[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
            all_constraints.append(A[i])
        # Add objective function -----------------------------------------------------------
        for i in range(nCols): 
            mkp.objective.set_linear([(i, c[i])])
    
        # Start time 
        timelim_cb.starttime = mkp.get_time()
        start_time = timelim_cb.starttime

        # Resolve the problem instance
        mkp.solve()
       
        # Report the results with 0 cut
        print_solution(mkp)
        logging.info("RELAXED PL SOLUTION (UPPER BOUND) IS %f",mkp.solution.get_objective_value())
        logging.info("Values: %s",mkp.solution.get_values())
        mkp.write(path_base_lp+"/0_cut.lp")
        mkp.solution.write(path_base_log+"/0_cut.log")
        

        # Generate gormory cuts
        n_cuts, b_bar = print_final_tableau(mkp)
        cuts, cut_limits = generate_gomory_cuts(n_cuts, nCols, nRows, mkp, names,b_bar)

        # Add the cuts sequentially and solve the problem
        for i in range(len(cuts)):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= cuts[i])], rhs= [cut_limits[i]], names = ["cut_"+str(i+1)], senses = [constraint_senses[i]])
            all_constraints.append(cuts[i])
            mkp.set_problem_name(name+"_cut_n"+str(i+1))
            logging.info("PRINT SOLUTION OF "+name+" WITH "+str(i+1)+" GOMORY CUTS APPLIED")
            mkp.solve()
            print_solution(mkp)
            mkp.write(path_base_lp+"/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/"+str(i+1)+"_cut.log")
        
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)


        mkp.end()
        pass