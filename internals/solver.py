from internals.utils import *
import logging
import cplex
import os

logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

def solveProblem(instance) :
    '''
    This function solves a specific problem instance
    
    Arguments:
        instance
    '''
    # Retrieve the matrixes of the problem instance
    c, A, b = getProblemData(instance) 
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

    # Variables 
    for i in range(nCols):
        names.append("x"+str(i))
        lower_bounds.append(0.0)
        upper_bounds.append(1.0)
    # Constraint 
    for i in range(nRows):
        constraint_names.append("c"+str(i))
        constraint_senses.append("L")

    logging.info("...Checking input coherency")
    assert(len(c)==nCols)
    logging.info("... Done.")

    # Slack 
    for i in range(nRows):
        names.append("s"+str(i))
        lower_bounds.append(0.0)

    nCols= nCols+nRows
    
    # Solver section    ############################################################

    #First of all determine the optimal solution
    determineOptimal(instance)

    with cplex.Cplex() as mkp,  open("cplexEvents.log", "w") as f:
        mkp.set_problem_name(name)
        mkp.objective.set_sense(mkp.objective.sense.maximize)
        mkp.set_log_stream(f)
        mkp.set_error_stream(f)
        mkp.set_warning_stream(f)
        mkp.set_results_stream(f)
        params = mkp.parameters
        # Disable presolve 
        params.preprocessing.presolve.set(0) 
        params.preprocessing.linear.set(0)
        params.preprocessing.reduce.set(0)
        # Register Callback 
        timelim_cb = mkp.register_callback(TimeLimitCallback)
        # Set time limit
        timelim_cb.timelimit = 60*3  #3 min max
        timelim_cb.aborted = False
        # Add variables & Slack --------------------------------------------------------------------
        mkp.variables.add(names=names)
        # Add variables 
        for i in range(nCols-nRows):
            mkp.variables.set_lower_bounds(i, lower_bounds[i])
            mkp.variables.set_upper_bounds(i, upper_bounds[i])
        # Add slack
        for i in range(nCols-nRows,nCols):
            mkp.variables.set_lower_bounds(i, lower_bounds[i])
        
        #Add slack to constraints
        A = A.tolist()
        for row in range(nRows) :
            for slack in range(nRows) : 
                if row==slack : 
                    A[row].append(1)
                else :
                    A[row].append(0)
        # Add contraints to Cplex ------------------------------------------------------------------
        for i in range(nRows):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])], rhs= [b[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
            all_constraints.append(A[i])
        # Add objective function -----------------------------------------------------------
        for i in range(nCols-nRows): 
            mkp.objective.set_linear([(i, c[i])])
    
        # Start time 
        timelim_cb.starttime = mkp.get_time()
        start_time = timelim_cb.starttime

        # Resolve the problem instance
        mkp.solve()
       
        # Report the results with 0 cut
        logging.info("\n\t\t\t\t\t\t*** RELAXED PL SOLUTION (UPPER BOUND) ***")
        print_solution(mkp)
        mkp.write(path_base_lp+"/0_cut.lp")
        mkp.solution.write(path_base_log+"/0_cut.log")

        # Generate gormory cuts
        n_cuts, b_bar = get_tableau(mkp)
        gc_lhs, gc_rhs = initialize_fract_gc(n_cuts, nCols, nRows, mkp, names,b_bar)
        cuts, cut_limits, cut_senses=generate_gc(mkp, A, gc_lhs, gc_rhs, names)

        # Add the cuts sequentially and solve the problem (without slack variables)
        for i in range(len(cuts)):
            mkp.linear_constraints.add(
                lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols-nRows)], val= cuts[i])], 
                senses= [cut_senses[i]], 
                rhs= [cut_limits[i]],
                names = ["cut_"+str(i+1)])
            all_constraints.append(cuts[i])
            mkp.set_problem_name(name+"_cut_n"+str(i+1))
            logging.info("\n\t\t\t\t\t Resolution of the problem called '"+name+"': "+str(i+1)+" Gomory cuts applied.")
            mkp.solve()
            print_solution(mkp)
            mkp.write(path_base_lp+"/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/"+str(i+1)+"_cut.log")
        
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)

        mkp.end()
        pass