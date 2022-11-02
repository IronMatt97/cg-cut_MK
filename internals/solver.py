from internals.utils import *
from internals.statistics import *
import logging
import cplex
import time
import os
import json
import pandas as pd

logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

def solveProblem(instance : str, cluster_type : str) :
    '''
    This function solves a specific problem instance
    
    Arguments:
        instance
        stats
    '''
    # Retrieve the matrixes of the problem instance
    c, A, b = getProblemData(instance) 
    nCols, nRows =(len(c)), (len(b))

    
    # Get the instance name
    txtname = instance.split("/")[2]    
    name = txtname.split(".txt")[0]
    if not os.path.exists("solutions/"+cluster_type+"/"+name):
            os.makedirs("solutions/"+cluster_type+"/"+name)
    if not os.path.exists("lp/"+cluster_type+"/"+name):
            os.makedirs("lp/"+cluster_type+"/"+name)
   
    path_base_log = str("solutions/"+cluster_type+"/"+name)
    path_base_lp = str("lp/"+cluster_type+"/"+name)

    # Get config params
    config = ConfigParser()
    config.read('config.ini')
    MAX_TIME=int(config[cluster_type]['MAX_TIME_PER_INSTANCE'])
    THRESHOLD = 0.05

    #Program variables section ####################################################
    names, lower_bounds, upper_bounds,constraint_senses,constraint_names =initializeInstanceVariables(nCols,nRows) 

    nCols= nCols+nRows

    # Populate statistics 
    tot_stats=[]

    # Solver section    ############################################################

    #First of all determine the optimal solution
    optimal_sol=determineOptimal(instance,cluster_type)
    # Define threshold
    threshold = optimal_sol * THRESHOLD
    lower = optimal_sol
    upper = optimal_sol + threshold
     
    with cplex.Cplex() as mkp,  open("cplexEvents.log", "w") as f:
        # set MKP
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
        # Add objective function -----------------------------------------------------------
        for i in range(nCols-nRows): 
            mkp.objective.set_linear([(i, c[i])])

        start_time = mkp.get_time()
        # Resolve the problem instance with 0 cuts
        mkp.solve()
        # Report the results with 0 cut
        logging.info("\n\t\t\t\t\t\t*** RELAXED PL SOLUTION (UPPER BOUND) ***")
        sol, sol_type,status = print_solution(mkp)
        if not os.path.exists(path_base_log+"/iteration0"):
            os.makedirs(path_base_log+"/iteration0")
        if not os.path.exists(path_base_lp+"/iteration0"):
            os.makedirs(path_base_lp+"/iteration0")
        mkp.write(path_base_lp+"/iteration0/0_cut.lp")
        mkp.solution.write(path_base_log+"/iteration0/0_cut.log")
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)
        #Append to statistics with 0 cuts
        tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,nRows,optimal_sol,sol,sol_type,status,0,elapsed_time,0, lower,upper))
        
        # Generate gormory cuts
        start_time = mkp.get_time()
        n_cuts, b_bar = get_tableau(mkp)
        gc_lhs, gc_rhs = initialize_fract_gc(n_cuts, nCols, mkp, names,b_bar)
        cuts, cut_limits, cut_senses=generate_gc(mkp, A, gc_lhs, gc_rhs, names)
        
        # Add the cuts sequentially and solve the problem (without slack variables)
        for i in range(len(cuts)):
            # Start time 
            mkp.linear_constraints.add(
                lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols-nRows)], val= cuts[i])], 
                senses= [cut_senses[i]], 
                rhs= [cut_limits[i]],
                names = ["cut_"+str(i+1)])
            mkp.set_problem_name(name+"_cut_n"+str(i+1))
            logging.info("\n\t\t\t\t\t Resolution of the problem called '"+name+"': "+str(i+1)+" Gomory cuts applied.")
            mkp.solve()
            sol,sol_type,status=print_solution(mkp)
            tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,(nRows+len(cuts)),optimal_sol,sol,sol_type,status,i+1,elapsed_time,1,lower,upper))
            if not os.path.exists(path_base_lp+"/iteration1"):
                os.makedirs(path_base_lp+"/iteration1")
            if not os.path.exists(path_base_log+"/iteration1"):
                os.makedirs(path_base_log+"/iteration1")
            mkp.write(path_base_lp+"/iteration1/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/iteration1/"+str(i+1)+"_cut.log")
            
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)
        mkp.end()
        pass
    
    start_time = time.time()
    elapsed_time = 0
    iteration = 1
    while ( not isSolInBounds(sol,upper,lower) and elapsed_time < MAX_TIME):
        iteration += 1
        sol,sol_type,status,cuts,cut_limits, tot_stats= iterateGomory(name,cluster_type,instance,cuts,cut_limits,tot_stats,optimal_sol,iteration,lower,upper)
        elapsed_time = time.time()-start_time

    return tot_stats

def iterateGomory(name,cluster_type,instance,cuts,cut_limits,tot_stats, optimal_sol, iteration,lower,upper):
    
    c, A, b = getProblemData(instance)
    newA = A.tolist()
    newB = b.tolist()
    for i in range(len(cuts)):
        newA.append(cuts[i])
        newB.append(cut_limits[i]) 
    
    A = np.asarray(newA,dtype=np.float64)
    b = np.asarray(newB,dtype=np.float64)

    nCols, nRows =(len(c)), (len(b))
    
    # Get the instance name
    path_base_log = str("solutions/"+cluster_type+"/"+name)
    path_base_lp = str("lp/"+cluster_type+"/"+name)

    if not os.path.exists(path_base_log+"/iteration"+str(iteration)):
                os.makedirs(path_base_log+"/iteration"+str(iteration))
    if not os.path.exists(path_base_lp+"/iteration"+str(iteration)):
                os.makedirs(path_base_lp+"/iteration"+str(iteration))

    #Program variables section ####################################################
    names, lower_bounds, upper_bounds,constraint_senses,constraint_names =initializeInstanceVariables(nCols,nRows) 
    nCols= nCols+nRows

    # Populate statistics 
    n_cuts = len(cuts)
    with cplex.Cplex() as mkp,  open("cplexEvents.log", "w") as f:
        # set mkp
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
        # Add objective function -----------------------------------------------------------
        for i in range(nCols-nRows): 
            mkp.objective.set_linear([(i, c[i])])
        # solve mkp
        mkp.solve()
        # get solution
        sol, sol_type,status = print_solution(mkp)
        mkp.write(path_base_lp+"/iteration"+str(iteration)+"/0_cut.lp")
        mkp.solution.write(path_base_log+"/iteration"+str(iteration)+"/0_cut.log")
        ########################################################################
        start_time = mkp.get_time()
        n_cuts, b_bar = get_tableau(mkp)
        gc_lhs, gc_rhs = initialize_fract_gc(n_cuts, nCols, mkp, names,b_bar)
        new_cuts, new_cut_limits, new_cut_senses=generate_gc(mkp, A, gc_lhs, gc_rhs, names)
        
        # Add the cuts sequentially and solve the problem (without slack variables)
        for i in range(len(new_cuts)):
            # Start time 
            mkp.linear_constraints.add(
                lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols-nRows)], val= new_cuts[i])], 
                senses= [new_cut_senses[i]], 
                rhs= [new_cut_limits[i]],
                names = ["cut_"+str(i+1)])
            mkp.set_problem_name(name+"_cut_n"+str(i+1))
            logging.info("\n\t\t\t\t\t Resolution of the problem called '"+name+"': "+str(i+1)+" Gomory cuts applied.")
            mkp.solve()
            sol,sol_type,status=print_solution(mkp)
            elapsed_time = time.time()-start_time
            tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,(nRows+len(cuts)),optimal_sol,sol,sol_type,status,n_cuts+i+1,elapsed_time,iteration,lower,upper))
            mkp.write(path_base_lp+"/iteration"+str(iteration)+"/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/iteration"+str(iteration)+"/"+str(i+1)+"_cut.log")
            
        for cut in new_cuts:
            cuts.append(cut)
        for cut_lim in new_cut_limits:
            cut_limits.append(cut_lim)

        sol,sol_type,status=print_solution(mkp)
        ########################################################################à
        mkp.end()
        pass

    return sol,sol_type,status,cuts,cut_limits,tot_stats