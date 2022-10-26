from internals.utils import MKPpopulate, print_solution , print_final_tableau, generate_gomory_cuts
import cplex


# This function solves a specific problem instance
def solveCplex(instance) :
    # Retrieve the matrixes of the problem instance
    c, A, b = MKPpopulate(instance) 
    nCols, nRows =(len(c)), (len(b))
    
    # Get the instance name
    txtname = instance.split("/")[1]    
    name = txtname.split(".txt")[0]
    cplexlog = name+".log"
    path_log = str("solutions/"+cplexlog)

    #Program variables section ####################################################

    names = []
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

    print("\t...Checking input coherency")
    assert(len(c)==len(lower_bounds))
    assert(len(c)==len(upper_bounds))
    assert(len(c)==len(names))
    print("\t\t... Done.")
    
    # Solver section    ############################################################
    with cplex.Cplex() as mkp:
        mkp.set_problem_name(name)
        mkp.objective.set_sense(mkp.objective.sense.maximize)
        params = mkp.parameters
        # Disable presolve 
        params.preprocessing.presolve.set(0) 
            
        # Add variables --------------------------------------------------------------------
        mkp.variables.add(names= ["x"+str(i) for i in range(nCols)])
    
        for i in range(nCols):
            mkp.variables.set_lower_bounds(i, lower_bounds[i])
            mkp.variables.set_upper_bounds(i, upper_bounds[i])

        # Add contraints -------------------------------------------------------------------
        for i in range(nRows):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])], rhs= [b[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])

        # Add objective function -----------------------------------------------------------
        for i in range(nCols): 
            mkp.objective.set_linear([(i, c[i])])
    
        # Resolve the problem instance
        mkp.solve()
       
        # Report the results
        print_solution(mkp)
        BinvA, n_cuts, b_bar = print_final_tableau(mkp)
        cuts, cut_limits = generate_gomory_cuts(n_cuts,nCols, nRows, mkp, names,b_bar)
        '''
        for i in range(len(cuts)):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= cuts[i])], rhs= [cut_limits[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
        mkp.solve()
        print_solution(mkp,mkp.solution.get_objective_value().is_integer())
        '''
        mkp.write("lp/"+name+".lp")
        mkp.solution.write(path_log)
        mkp.end()
        pass

'''
    with cplex.Cplex() as mkp:
        mkp.set_problem_name(name)
        mkp.objective.set_sense(mkp.objective.sense.maximize)
        params = mkp.parameters
        # Disable presolve 
        params.preprocessing.presolve.set(0) 
            
        # Add variables --------------------------------------------------------------------
        mkp.variables.add(names= ["x"+str(i) for i in range(nCols)])
    
        for i in range(nCols):
            mkp.variables.set_lower_bounds(i, lower_bounds[i])
            mkp.variables.set_upper_bounds(i, upper_bounds[i])

        # Add contraints -------------------------------------------------------------------
        for i in range(nRows):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= A[i])], rhs= [b[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
        for i in range(len(cuts)):
            mkp.linear_constraints.add(lin_expr= [cplex.SparsePair(ind= [j for j in range(nCols)], val= cuts[i])], rhs= [cut_limits[i]], names = [constraint_names[i]], senses = [constraint_senses[i]])
    
        # Add objective function -----------------------------------------------------------
        for i in range(nCols): 
            mkp.objective.set_linear([(i, c[i])])
    
        # Resolve the problem instance
        mkp.solve()
    
        # Report the results
        print_solution(mkp,mkp.solution.get_objective_value().is_integer())
        mkp.write("lp/"+name+".lp")
        mkp.solution.write(path_log)
        mkp.end()
        pass
'''
