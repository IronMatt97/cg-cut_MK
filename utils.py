import utils
from docplex.mp.model import Model
from typing import Tuple
import numpy as np
from cplex._internal._subinterfaces import CutType
import sys

def MKPpopulate(name: str) -> Tuple:
    # populateMKP

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
    
    # Opening .txt file to read raw data of an instance
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