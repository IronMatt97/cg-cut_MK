from cplex.callbacks import MIPInfoCallback
from typing import Tuple
import numpy as np
import fractions
import logging
import cplex
import io


logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

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

def flushLog(logName):
    with open(logName,'w') as file:
        pass

# Function to extract A, b and c (constraint coefficients matrix, right hand side array and objective function coefficients array)
def getProblemData(name: str) -> Tuple:
    # Opening .txt file in order to read the raw data of a problem instance
    file = open(str(name), 'r')
    x = []
    for line in file:
        splitLine = line.split()
        for i in range(len(splitLine)):
            x.append(splitLine[i])
    file.close()
    
    # Define parameters
    NumColumns, NumRows = int(x.pop(0)), int(x.pop(0))
    logging.info('This instance has %d variables and %d constraints' %(NumColumns, NumRows))

    # Populating Objective Function Coefficients
    c = np.array([float(x.pop(0)) for i in range(NumColumns)])
    assert type(c) == np.ndarray
    assert len(c)  == NumColumns
    
    # Populating A matrix (size NumRows * NumColumns)
    ConstCoef = np.array([float(x.pop(0)) for i in range(int(NumRows * NumColumns))])    
    assert type(ConstCoef) == np.ndarray
    assert len(ConstCoef)  == int(NumRows*NumColumns)
    
    # reshaping the 1-d ConstCoef into A
    A = np.reshape(ConstCoef, (NumRows, NumColumns)) 
    assert A.shape == (NumRows, NumColumns)
    
    # Populating the RHS
    b = np.array([float(x.pop(0)) for i in range(int(NumRows))])
    assert len(b) == NumRows
    assert type(b) == np.ndarray

    return (c, A, b)

def print_solution(prob):
    ncol = len(prob.variables.get_cols())
    nrow = len(prob.linear_constraints.get_rows())
    varnames = prob.variables.get_names()
    slack = np.round(prob.solution.get_linear_slacks(), 3)
    x = np.round(prob.solution.get_values(), 3)

    # Log everything about the solutions found
    logging.info("\t-> Solution status = %s", prob.solution.status[prob.solution.get_status()])
    logging.info("\t-> Solution value  = %f\n", prob.solution.get_objective_value())
    logging.info("SLACKS SITUATION:")
    for i in range(nrow):
        logging.info(f'-> Row {i}:  Slack = {slack[i]}')
    logging.info("\n\t\t\t\t\t PROBLEM VARIABLES:")
    for j in range(ncol):
        logging.info(f'-> Column {j} (variable {varnames[j]}):  Value = {x[j]}')

def get_tableau(prob):
    BinvA = np.array(prob.solution.advanced.binvarow())

    nrow = BinvA.shape[0]
    ncol = BinvA.shape[1]
    b_bar = np.zeros(nrow)
    varnames = prob.variables.get_names()
    b = prob.linear_constraints.get_rhs()
    Binv = np.array(prob.solution.advanced.binvrow())
    b_bar = np.matmul(Binv, b)
    idx = 0     # Compute the nonzeros
    n_cuts = 0  # Number of fractional variables (cuts to be generated)
    logging.info('\n\t\t\t\t\t LP relaxation final tableau:\n')
    for i in range(nrow):
        output_t = io.StringIO()
        z = prob.solution.advanced.binvarow(i)
        for j in range(ncol):
            if z[j] > 0:
                print('+', end='',file=output_t)
            zj = fractions.Fraction(z[j]).limit_denominator()
            num = zj.numerator
            den = zj.denominator
            if num != 0 and num != den:
                print(f'{num}/{den} {varnames[j]} ', end='',file=output_t)
            elif num == den:
                print(f'{varnames[j]} ', end='',file=output_t)
            if np.floor(z[j]+0.5) != 0:
                idx += 1
        b_bar_i = fractions.Fraction(b_bar[i]).limit_denominator()
        num = b_bar_i.numerator
        den = b_bar_i.denominator
        print(f'= {num}/{den}',file=output_t)
        contents = output_t.getvalue()
        logging.info("%s",contents)
        output_t.close()
        # Count the number of cuts to be generated
        if np.floor(b_bar[i]) != b_bar[i]:
            n_cuts += 1    
    
    logging.info("Cuts to generate: %d", n_cuts)
    return n_cuts , b_bar

def initialize_fract_gc(n_cuts,ncol, nrow, prob, varnames, b_bar) : 
    cuts = []
    cut_limits= []
    gc_sense = [''] * n_cuts
    gc_rhs   = np.zeros(n_cuts)
    gc_lhs   = np.zeros([n_cuts, ncol])
    rmatbeg  = np.zeros(n_cuts)
    rmatind  = np.zeros(ncol)
    rmatval  = np.zeros(ncol)
    logging.info('Generating Gomory cuts...\n')
    cut = 0  #  Index of cut to be added
    for i in range(nrow):
        idx = 0
        output = io.StringIO()
        if np.floor(b_bar[i]) != b_bar[i]:
            print(f'Row {i+1} gives cut -> ', end = '', file=output)
            z = np.copy(prob.solution.advanced.binvarow(i)) # Use np.copy to avoid changing the
                                                        # optimal tableau in the problem instance
            rmatbeg[cut] = idx
            cuts.append([])
            for j in range(ncol):
                z[j] = z[j] - np.floor(z[j])              
                if z[j] != 0:
                    rmatind[idx] = j
                    rmatval[idx] = z[j]
                    idx +=1
                # Print the cut
                if z[j] > 0:
                    print('+', end = '',file=output)
                if (z[j] != 0):
                        fj = fractions.Fraction(z[j])
                        fj = fj.limit_denominator()
                        num, den = (fj.numerator, fj.denominator)
                        print(f'{num}/{den} {varnames[j]} ', end='',file=output)
                gc_lhs[i,:] = z
                cuts[i].append(z[j])
            
            gc_rhs[cut] = b_bar[i] - np.copy(np.floor(b_bar[i])) # np.copy as above
            gc_sense[cut] = 'L'
            gc_rhs_i = fractions.Fraction(gc_rhs[cut]).limit_denominator()
            num = gc_rhs_i.numerator
            den = gc_rhs_i.denominator
            print(f'>= {num}/{den}',file=output)
            cut_limits.append(gc_rhs[cut])
            cut += 1
            contents = output.getvalue()
            output.close()
            logging.info(contents)
   
    return gc_lhs, gc_rhs

def generate_gc(mkp, A, gc_lhs, gc_rhs, names) : 
    logging.info('*** GOMORY CUTS ***\n')
    cuts = []
    cuts_limits = []
    cut_senses = []
    for i, gc in enumerate(gc_lhs):
        output = io.StringIO()
        cuts.append([])
        lhs, rhs = get_lhs_rhs(mkp, gc_lhs[i], gc_rhs[i], A)
        # Print the cut
        for j in range(len(lhs)):
            if -lhs[j] > 0:
                print('+', end = '',file=output)
            if (-lhs[j] != 0):
                print(f'{-lhs[j]} {names[j]} ', end='',file=output)
                cuts[i].append(-lhs[j])
            if (-lhs[j] == 0):
                print(f'{-lhs[j]} {names[j]} ', end='',file=output)
                cuts[i].append(0)
        print(f'<= {-rhs[0]}\n', end='',file=output)
        cuts_limits.append(-rhs[0])
        cut_senses.append('L')
        contents = output.getvalue()
        output.close()
        logging.info(contents)
    return cuts, cuts_limits, cut_senses

def get_lhs_rhs(prob, cut_row, cut_rhs, A):
    ncol = len(A[0])
    cut_row = np.append(cut_row, cut_rhs)
    b = np.array(prob.linear_constraints.get_rhs())
    A = np.append(A, b.reshape(-1, 1), axis=1)
    plotted_vars = np.nonzero(prob.objective.get_linear())[0]
    # Assumption: plotted variables are at the beginning of the initial tableau
    for i, sk in enumerate(range(len(plotted_vars), ncol)):
        cut_coef = cut_row[sk]
        cut_row -= A[i,:] * cut_coef
    lhs = cut_row[:len(plotted_vars)]
    rhs = cut_row[ncol:]
    return lhs, rhs

def determineOptimal(instance):
    c, A, b = getProblemData(instance) 
    nCols, nRows = (len(c), len(b))
    # Get the instance name
    txtname = instance.split("/")[1]    
    name = txtname.split(".txt")[0]
    cplexlog = name+".log"
    #Program variables section ####################################################
    names = []
    all_constraints = []
    constraint_names = []
    constraint_senses = []
    # Variables 
    for i in range(nCols):
        names.append("x"+str(i))
    # Constraint 
    for i in range(nRows):
        constraint_names.append("c"+str(i))
        constraint_senses.append("L")
    with cplex.Cplex() as mkp,  open("optimalResolution.log", "w") as f:
        mkp.set_problem_name(name)
        mkp.objective.set_sense(mkp.objective.sense.maximize)
        mkp.set_log_stream(f)
        mkp.set_error_stream(f)
        mkp.set_warning_stream(f)
        mkp.set_results_stream(f)
        params = mkp.parameters
        # Disable presolve 
        params.preprocessing.presolve.set(0) 
        # Add variables & Slack --------------------------------------------------------------------
        mkp.variables.add(names=names, types=[mkp.variables.type.binary] * nCols)
        # Add contraints -------------------------------------------------------------------
        for i in range(nRows):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])], rhs= [b[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
            all_constraints.append(A[i])
        # Add objective function -----------------------------------------------------------
        for i in range(nCols): 
            mkp.objective.set_linear([(i, c[i])])
        # Resolve the problem instance
        mkp.solve()
        # Report the results 
        logging.info("\n\t\t\t\t\t\t*** OPTIMAL PLI SOLUTION ***")
        print_solution(mkp)
        mkp.write("lp/"+name+"/optimal.lp")
        mkp.solution.write("solutions/"+name+"/optimal.log")
