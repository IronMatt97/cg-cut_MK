from docplex.mp.model import Model
from typing import Tuple
import numpy as np
import fractions
from cplex._internal._subinterfaces import CutType
import sys
import cplex

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
    NumColumns, NumRows, BestOF = int(x.pop(0)), int(x.pop(0)), float(x.pop(0))
    print('This instance has %d variables and %d constraints' %(NumColumns, NumRows))

    if BestOF != float(0):
        print('Best known integer objective value for this instance = ', BestOF)
    else:
        print('Best integer objective value for this instance is not indicated')
    
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

def get_cut_stats(mdl):
    """ Computes a dicitonary of cut name -> number of cuts used
    Args:
        mdl: an instance of `docplex.mp.Model`
    Returns:
        a dictionary of string -> int,, from cut type to number used (nonzero).
        Unused cut types ar enot mentioned
    Example:
        For delivered model "nurses"
        # {'cover': 88, 'GUB_cover': 9, 'flow_cover': 6, 'fractional': 5, 'MIR': 9, 'zero_half': 9, 'lift_and_project': 5}
    """
    cut_stats = {}
    cpx = mdl.cplex
    cut_type_instance = CutType()
    for ct in cut_type_instance:
        num = cpx.solution.MIP.get_num_cuts(ct)
        if num:
            cutname = cut_type_instance[ct]
            cut_stats[cutname] = num

    return cut_stats


def print_solution(prob, is_integer = False):
    ncol = len(prob.variables.get_cols())
    nrow = len(prob.linear_constraints.get_rows())
    varnames = prob.variables.get_names()
    # solution.get_status() returns an integer code
    print('Solution status = ' , prob.solution.get_status(), ':')
    # the following line prints the corresponding string
    print(prob.solution.status[prob.solution.get_status()])
    print('Solution value  = ', prob.solution.get_objective_value())
    slack = np.round(prob.solution.get_linear_slacks(), 3)
    x     = np.round(prob.solution.get_values(), 3)
    for i in range(nrow):
        print(f'Row {i}:  Slack = {slack[i]}')
    for j in range(ncol):
        print(f'Column {j} (variable {varnames[j]}):  Value = {x[j]}')



def print_final_tableau(prob):
    BinvA = np.array(prob.solution.advanced.binvarow())

    nrow = BinvA.shape[0]
    ncol = BinvA.shape[1]
    b_bar = np.zeros(nrow)
    varnames = prob.variables.get_names()
    b = prob.linear_constraints.get_rhs()
    Binv = np.array(prob.solution.advanced.binvrow())
    b_bar = np.matmul(Binv, b)


    print('\n\nFinal tableau:')
    idx = 0     # Compute the nonzeros
    n_cuts = 0  # Number of fractional variables (cuts to be generated)
    for i in range(nrow):
        z = prob.solution.advanced.binvarow(i)
        for j in range(ncol):
            if z[j] > 0:
                print('+', end='')
            zj = fractions.Fraction(z[j]).limit_denominator()
            num = zj.numerator
            den = zj.denominator
            if num != 0 and num != den:
                print(f'{num}/{den} {varnames[j]} ', end='')
            elif num == den:
                print(f'{varnames[j]} ', end='')
            if np.floor(z[j]+0.5) != 0:
                idx += 1
        b_bar_i = fractions.Fraction(b_bar[i]).limit_denominator()
        num = b_bar_i.numerator
        den = b_bar_i.denominator
        print(f'= {num}/{den}\n')
        # Count the number of cuts to be generated
        if np.floor(b_bar[i]) != b_bar[i]:
            n_cuts += 1    
    print(f'Cuts to generate: {n_cuts}')
    return BinvA, n_cuts , b_bar


def get_A_matrix(prob):
    rows = prob.linear_constraints.get_rows()
    nrow = len(rows)
    ncol = max([max(r.ind) for r in rows]) + 1

    A = np.zeros((nrow, ncol))
    for i, r in enumerate(prob.linear_constraints.get_rows()):
        for j in range(ncol):
            if j in r.ind:
                A[i, j] = r.val[r.ind.index(j)]
    return A

def get_p9(is_integer = False, is_standard = True):
    f      = [-1, -1, 0, 0, 0]
    varnames = ['x1', 'x2', 's1', 's2', 's3']
    b      = [5, 7, 26]
    rownames = ['c1', 'c2', 'c3']
    sense    = 'EEE'
    if is_integer:
        types = 'IICCC'
    else:
        types = 'CCCCC'
    rows = [[['x1','x2', 's1', 's2', 's3'],[-2, 2, 1, 0, 0]],
            [[0, 1, 2, 3, 4],[ 0, 2, 0, 1, 0]],
            [[0, 1, 2, 3, 4],[ 5, 2, 0, 0, 1]]]
    if not is_standard:
        true_vars = np.nonzero(f)[0]
        true_vars = true_vars.shape[0]
        f = f[:true_vars]
        varnames = varnames[:true_vars]
        types = types[:true_vars]
        rows = [[a[:true_vars], b[:true_vars]] for a, b in rows]
        sense = 'LLL'    
    nrow = len(rownames)
    ncol = len(varnames)
    prob = cplex.Cplex()
    if is_integer:
        print("integer")
        prob.variables.add(obj = f, names = varnames, types = types)
    else:
        print("no integer")
        prob.variables.add(obj = f, names = varnames)
    prob.linear_constraints.add(lin_expr = rows, senses = sense,
                                rhs = b, names = rownames)
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.parameters.preprocessing.presolve.set(0)
    return prob

def get_plottable_cut(prob, cut_row, cut_rhs, A, ncol):
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


def generate_gomory_cuts(n_cuts,ncol, nrow, prob, varnames, b_bar) : 
    cuts = []
    gc_sense = [''] * n_cuts
    gc_rhs   = np.zeros(n_cuts)
    gc_lhs   = np.zeros([n_cuts, ncol])
    rmatbeg  = np.zeros(n_cuts)
    rmatind  = np.zeros(ncol)
    rmatval  = np.zeros(ncol)
    print('\nGenerated Gomory cuts:\n')
    #idx = 0
    cut = 0  #  Index of cut to be added
    for i in range(nrow):
        idx = 0
        if np.floor(b_bar[i]) != b_bar[i]:
            print(f'Row {i+1} gives cut -> ', end = '')
            z = np.copy(prob.solution.advanced.binvarow(i)) # Use np.copy to avoid changing the
                                                        # optimal tableau in the problem instance
            rmatbeg[cut] = idx
            for j in range(ncol):
                z[j] = z[j] - np.floor(z[j])              
                if z[j] != 0:
                    rmatind[idx] = j
                    rmatval[idx] = z[j]
                    idx +=1
                # Print the cut
                if z[j] > 0:
                    print('+', end = '')
                if (z[j] != 0):
                        fj = fractions.Fraction(z[j])
                        fj = fj.limit_denominator()
                        num, den = (fj.numerator, fj.denominator)
                        print(f'{num}/{den} {varnames[j]} ', end='')
                gc_lhs[i,:] = z
            
            gc_rhs[cut] = b_bar[i] - np.copy(np.floor(b_bar[i])) # np.copy as above
            gc_sense[cut] = 'L'
            gc_rhs_i = fractions.Fraction(gc_rhs[cut]).limit_denominator()
            num = gc_rhs_i.numerator
            den = gc_rhs_i.denominator
            print(f'>= {num}/{den}\n')
            cut += 1
    return cuts
## funzione che ritorna cut 