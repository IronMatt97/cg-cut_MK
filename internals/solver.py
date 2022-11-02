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
        setMKP(mkp,name,f,names,nCols,nRows,lower_bounds,upper_bounds,constraint_senses,constraint_names,A,b,c)
        start_time = mkp.get_time()
        # Resolve the problem instance with 0 cuts
        mkp.solve()
        # Report the results with 0 cut
        logging.info("\n\t\t\t\t\t\t*** RELAXED PL SOLUTION (UPPER BOUND) ***")
        sol, sol_type,status = print_solution(mkp)
        
        mkp.write(path_base_lp+"/0_cut.lp")
        mkp.solution.write(path_base_log+"/0_cut.log")
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)
        #Append to statistics with 0 cuts
        tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,nRows,optimal_sol,sol,sol_type,status,0,elapsed_time,0, lower,upper))
        
        # Generate gormory cuts
        start_time = mkp.get_time()
        cuts, cut_limits, cut_senses= applyGomory(mkp, nCols,names,A)
        
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
            mkp.write(path_base_lp+"/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/"+str(i+1)+"_cut.log")
            
        end_time = mkp.get_time()
        elapsed_time = end_time-start_time
        logging.info("Elapsed time: %f ", elapsed_time)
        tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,(nRows+len(cuts)),optimal_sol,sol,sol_type,status,len(cuts),elapsed_time,1,lower,upper))
        mkp.end()
        pass
    
    start_time = time.time()
    elapsed_time = 0
    iteration = 1
    while ( not isSolInBounds(sol,upper,lower) and elapsed_time < MAX_TIME):
        iteration += 1
        sol,sol_type,status,cuts,cut_limits = iterateGomory(name,cluster_type,instance,cuts,cut_limits)
        elapsed_time = time.time()-start_time
        tot_stats.append(getStatistics(name,cluster_type,nCols-nRows,(nRows+len(cuts)),optimal_sol,sol,sol_type,status,len(cuts),elapsed_time,iteration,lower,upper))

    return tot_stats

def iterateGomory(name,cluster_type,instance,cuts,cut_limits):

    c, A, b = getProblemData(instance)
    for i in range(len(cuts)):
        A.tolist().append(cuts[i])
        b.tolist().append(cut_limits[i]) 
    nCols, nRows =(len(c)), (len(b))
    
    # Get the instance name
    path_base_log = str("solutions/"+cluster_type+"/"+name)
    path_base_lp = str("lp/"+cluster_type+"/"+name)

    #Program variables section ####################################################
    names, lower_bounds, upper_bounds,constraint_senses,constraint_names =initializeInstanceVariables(nCols,nRows) 
    nCols= nCols+nRows

    # Populate statistics 

    with cplex.Cplex() as mkp,  open("cplexEvents.log", "w") as f:
        # set mkp
        setMKP(mkp,name,f,names,nCols,nRows,lower_bounds,upper_bounds,constraint_senses,constraint_names,A,b,c)
        # solve mkp
        mkp.solve()
        # get solution
        sol, sol_type,status = print_solution(mkp)
        mkp.write(path_base_lp+"/0_cut.lp")
        mkp.solution.write(path_base_log+"/0_cut.log")
        ########################################################################à
        new_cuts, new_cut_limits, new_cut_senses= applyGomory(mkp, nCols,names,A)
        
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
            mkp.write(path_base_lp+"/"+str(i+1)+"_cut.lp")
            mkp.solution.write(path_base_log+"/"+str(i+1)+"_cut.log")
            
        for cut in new_cuts:
            cuts.append(cut)
        for cut_lim in new_cut_limits:
            cut_limits.append(cut_lim)

        sol,sol_type,status=print_solution(mkp)
        ########################################################################à
        mkp.end()
        pass

    return sol,sol_type,status,cuts,cut_limits