from distutils.archive_util import make_zipfile
from docplex.mp.model import Model
from typing import Tuple
import numpy as np
import fractions
from cplex._internal._subinterfaces import CutType
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

        
def MKPpopulate(name: str) -> Tuple:
    '''
    This function extracts the raw data from a .txt file and populates the objective function coefficients
    array, the constraints coefficients matrix A and the right hand side b array
    
    Arguments:
        name -- the name of the .txt file that contains the raw data
        
    returns:
        c -- objective function coefficients array (shape = 1 * n)
        A -- constraints coefficients matrix A (shape = m * n)
        b -- right hand side values (shape = 1 * m)
    '''
    
    # Opening .txt file in order to read the raw data of an instance
    file = open(str(name), 'r')
    x = []
    for line in file:
        splitLine = line.split()
        for i in range(len(splitLine)):
            x.append(splitLine[i])
    file.close()
    
    # Define parameters
    NumColumns, NumRows = int(x.pop(0)), int(x.pop(0))
    print('This instance has %d variables and %d constraints' %(NumColumns, NumRows))

    # Populating Objective Function Coefficients
    c = np.array([float(x.pop(0)) for i in range(NumColumns)])
    
    assert type(c) == np.ndarray
    assert len(c)  == NumColumns
    
    # Populating A matrix (size NumRows * NumColumns)
    ConstCoef = np.array([float(x.pop(0)) for i in range(int(NumRows * NumColumns))])    
    
    assert type(ConstCoef) == np.ndarray
    assert len(ConstCoef)  == int(NumRows*NumColumns)
    
    A = np.reshape(ConstCoef, (NumRows, NumColumns)) # reshaping the 1-d ConstCoef into A
    
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
    # solution.get_status() returns an integer code
    #print('Solution status = ' , prob.solution.get_status(), ':')
    # the following line prints the corresponding string
    #print(prob.solution.status[prob.solution.get_status()])
    print('Solution value  = ', prob.solution.get_objective_value())
    slack = np.round(prob.solution.get_linear_slacks(), 3)
    x     = np.round(prob.solution.get_values(), 3)
    print("Variables solution: ",x)
    #for i in range(nrow):
    #    print(f'Row {i}:  Slack = {slack[i]}')
    #for j in range(ncol):
    #    print(f'Column {j} (variable {varnames[j]}):  Value = {x[j]}')



def print_final_tableau(prob):
    BinvA = np.array(prob.solution.advanced.binvarow())

    nrow = BinvA.shape[0]
    ncol = BinvA.shape[1]
    b_bar = np.zeros(nrow)
    varnames = prob.variables.get_names()
    b = prob.linear_constraints.get_rhs()
    Binv = np.array(prob.solution.advanced.binvrow())
    b_bar = np.matmul(Binv, b)


    #print('\n\nFinal tableau:')
    idx = 0     # Compute the nonzeros
    n_cuts = 0  # Number of fractional variables (cuts to be generated)
    for i in range(nrow):
        z = prob.solution.advanced.binvarow(i)
        for j in range(ncol):
            #if z[j] > 0:
                #print('+', end='')
            zj = fractions.Fraction(z[j]).limit_denominator()
            num = zj.numerator
            den = zj.denominator
            #if num != 0 and num != den:
            #    print(f'{num}/{den} {varnames[j]} ', end='')
            #elif num == den:
            #    print(f'{varnames[j]} ', end='')
            if np.floor(z[j]+0.5) != 0:
                idx += 1
        b_bar_i = fractions.Fraction(b_bar[i]).limit_denominator()
        num = b_bar_i.numerator
        den = b_bar_i.denominator
        #print(f'= {num}/{den}\n')
        # Count the number of cuts to be generated
        if np.floor(b_bar[i]) != b_bar[i]:
            n_cuts += 1    
    print(f'Cuts to generate: {n_cuts}')
    return n_cuts , b_bar

def generate_gomory_cuts(n_cuts,ncol, nrow, prob, varnames, b_bar) : 
    cuts = []
    cut_limits= []
    gc_sense = [''] * n_cuts
    gc_rhs   = np.zeros(n_cuts)
    gc_lhs   = np.zeros([n_cuts, ncol])
    rmatbeg  = np.zeros(n_cuts)
    rmatind  = np.zeros(ncol)
    rmatval  = np.zeros(ncol)
    #print('\nGenerated Gomory cuts:\n')
    #idx = 0
    cut = 0  #  Index of cut to be added
    for i in range(nrow):
        idx = 0
        if np.floor(b_bar[i]) != b_bar[i]:
            #print(f'Row {i+1} gives cut -> ', end = '')
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
                #if z[j] > 0:
                #    print('+', end = '')
                if (z[j] != 0):
                        fj = fractions.Fraction(z[j])
                        fj = fj.limit_denominator()
                        num, den = (fj.numerator, fj.denominator)
                #        print(f'{num}/{den} {varnames[j]} ', end='')
                gc_lhs[i,:] = z
                cuts[i].append(z[j])
            
            gc_rhs[cut] = b_bar[i] - np.copy(np.floor(b_bar[i])) # np.copy as above
            gc_sense[cut] = 'L'
            gc_rhs_i = fractions.Fraction(gc_rhs[cut]).limit_denominator()
            num = gc_rhs_i.numerator
            den = gc_rhs_i.denominator
            #print(f'>= {num}/{den}\n')
            cut_limits.append(gc_rhs[cut])
            cut += 1
    return cuts, cut_limits

def determineOptimal(instance):
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
    return mkp.solution._objective, mkp.solution.get_values
