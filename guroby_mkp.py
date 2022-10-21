#!/usr/bin/env python3
import sys
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

def mycallback(model, where):
    if where == GRB.Callback.POLLING:
        # Ignore polling callback
        pass
    elif where == GRB.Callback.PRESOLVE:
        # Presolve callback
        print("PRESOLVE")
        return

        cdels = model.cbGet(GRB.Callback.PRE_COLDEL)
        rdels = model.cbGet(GRB.Callback.PRE_ROWDEL)
        if cdels or rdels:
            print('%d columns and %d rows are removed' % (cdels, rdels))
    elif where == GRB.Callback.SIMPLEX:
        # Simplex callback
        print("SIMPLEX")
        itcnt = model.cbGet(GRB.Callback.SPX_ITRCNT)
        if itcnt - model._lastiter >= 100:
            model._lastiter = itcnt
            obj = model.cbGet(GRB.Callback.SPX_OBJVAL)
            ispert = model.cbGet(GRB.Callback.SPX_ISPERT)
            pinf = model.cbGet(GRB.Callback.SPX_PRIMINF)
            dinf = model.cbGet(GRB.Callback.SPX_DUALINF)
            if ispert == 0:
                ch = ' '
            elif ispert == 1:
                ch = 'S'
            else:
                ch = 'P'
            print('%d %g%s %g %g' % (int(itcnt), obj, ch, pinf, dinf))
    elif where == GRB.Callback.MIP:
        print("MIP")
        # General MIP callback
        nodecnt = model.cbGet(GRB.Callback.MIP_NODCNT)
        objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
        objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
        solcnt = model.cbGet(GRB.Callback.MIP_SOLCNT)
        if nodecnt - model._lastnode >= 100:
            model._lastnode = nodecnt
            actnodes = model.cbGet(GRB.Callback.MIP_NODLFT)
            itcnt = model.cbGet(GRB.Callback.MIP_ITRCNT)
            cutcnt = model.cbGet(GRB.Callback.MIP_CUTCNT)
            print('%d %d %d %g %g %d %d' % (nodecnt, actnodes,
                  itcnt, objbst, objbnd, solcnt, cutcnt))
        if abs(objbst - objbnd) < 0.1 * (1.0 + abs(objbst)):
            print('Stop early - 10% gap achieved')
            model.terminate()
        if nodecnt >= 10000 and solcnt:
            print('Stop early - 10000 nodes explored')
            model.terminate()
    elif where == GRB.Callback.MIPSOL:
        # MIP solution callback
        print("MIPSOL")
        nodecnt = model.cbGet(GRB.Callback.MIPSOL_NODCNT)
        obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
        solcnt = model.cbGet(GRB.Callback.MIPSOL_SOLCNT)
        x = model.cbGetSolution(model._vars)
        print('**** New solution at node %d, obj %g, sol %d, '
              'x[0] = %g ****' % (nodecnt, obj, solcnt, x[0]))
    elif where == GRB.Callback.MIPNODE:
        # MIP node callback
        print('**** New node ****')
        if model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL:
            x = model.cbGetNodeRel(model._vars)
            model.cbSetSolution(model.getVars(), x)
    elif where == GRB.Callback.BARRIER:
        # Barrier callback
        itcnt = model.cbGet(GRB.Callback.BARRIER_ITRCNT)
        primobj = model.cbGet(GRB.Callback.BARRIER_PRIMOBJ)
        dualobj = model.cbGet(GRB.Callback.BARRIER_DUALOBJ)
        priminf = model.cbGet(GRB.Callback.BARRIER_PRIMINF)
        dualinf = model.cbGet(GRB.Callback.BARRIER_DUALINF)
        cmpl = model.cbGet(GRB.Callback.BARRIER_COMPL)
        print('%d %g %g %g %g %g' % (itcnt, primobj, dualobj,
              priminf, dualinf, cmpl))
    elif where == GRB.Callback.MESSAGE:
        # Message callback
        msg = model.cbGet(GRB.Callback.MSG_STRING)
        model._logfile.write(msg)

       
    
def addGomoryCut(j,m):

	x=m.getVars()
	n=len(x)
	B, NB = [], []
	for i in range(n):
		B.append(i) if (x[i].x == 1) else NB.append(i)
	# Add binary cut to Model
	m.addConstr((gp.quicksum(x[i] for i in B) - gp.quicksum(x[j] for j in NB)) <= len(B) - 1, name="binaryCut{}".format(j))
	m.update()
	m.setParam(GRB.Param.Cuts, m.params.Cuts+1);
	print("addGomory executed\n")


def CreateModel(n,p,w,v,wc,vc):
   # create empty model
   m = gp.Model()
   
   # add decision variables
   x = m.addVars(n, vtype=GRB.INTEGER, name='x')
   # set objective function
   m.setObjective(gp.quicksum(p[i] * x[i] for i in range(n)), GRB.MAXIMIZE)
   # add constraint
   m.addConstr((gp.quicksum(w[i] * x[i] for i in range(n)) <= wc), name="knapsack-w")
   m.addConstr((gp.quicksum(v[i] * x[i] for i in range(n)) <= vc), name="knapsack-v")
   # Add Lazy Constraints
   m.update()
   # quiet gurobi
   m.setParam(GRB.Param.LogToConsole,0)
   m.setParam(GRB.Param.PreCrush,0)
   m.setParam(GRB.Param.Presolve,0)
   m.setParam(GRB.Param.Cuts, 0)
   m.setParam('OutputFlag', 0)
   m.setParam('Heuristics', 0)
   
   print("create model executed\n")
   return m

def SolveModel(m) : 
	m._vars = m.getVars()
	m.optimize(mycallback)
	m.write("knapsack.lp")

def main(): 
    n = 2  #number of items
    p = [1,4]  #profits
    w = [2, 4]  #weights
    v = [5, 3]  #volumes
    wc = 12  #capacity (weight)
    vc = 15  #capacity (volume)
    logfile = open('cb.log', 'w')
    m=CreateModel(n,p,w,v,wc,vc)
    m._lastiter = -GRB.INFINITY
    m._lastnode = -GRB.INFINITY
    m._logfile = logfile
    SolveModel(m)
    logfile.close()
    printSolution(m)

def printSolution(model):
    if model.SolCount == 0:
        print('No solution found, optimization status = %d' % model.Status)
    else:
        print('Solution found, objective = %g' % model.ObjVal)
        for v in model.getVars():
            if v.X != 0.0:
                print('%s %g' % (v.VarName, v.X))
                
if __name__ == '__main__':
   main()
