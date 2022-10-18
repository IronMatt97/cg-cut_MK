#!/usr/bin/env python3
import sys
import gurobipy as gp
from gurobipy import GRB
import pandas as pd


def addBinaryCut(j,m):
	x=m.getVars()
	n=len(x)
	B, NB = [], []
	for i in range(n):
		B.append(i) if (x[i].x == 1) else NB.append(i)
	# Add binary cut to Model
	m.addConstr((gp.quicksum(x[i] for i in B) - gp.quicksum(x[j] for j in NB)) <= len(B) - 1, name="binaryCut{}".format(j))
	m.update()
	print("addBinary executed")


def CreateModel(n,p,w,v,wc,vc):
   # create empty model
   m = gp.Model()
   # add decision variables
   x = m.addVars(n, vtype=GRB.BINARY, name='x')
   # set objective function
   m.setObjective(gp.quicksum(p[i] * x[i] for i in range(n)), GRB.MAXIMIZE)
   # add constraint
   m.addConstr((gp.quicksum(w[i] * x[i] for i in range(n)) <= wc), name="knapsack-w")
   m.addConstr((gp.quicksum(v[i] * x[i] for i in range(n)) <= vc), name="knapsack-v")
   # Add Lazy Constraints
   m.update()
   # quiet gurobi
   m.setParam(GRB.Param.LogToConsole, 0)
   print("create model executed")
   return m


def SolveModel(m) : 
	searchBool = True
	k = 1
	while searchBool:
		# solve the model
		m.optimize()
		if m.Status == GRB.OPTIMAL:
			if k == 1:
				zopt = m.ObjVal
			znew = m.ObjVal if (k > 1) else zopt
			if znew == zopt:
				# Found new feasible optimal solution
				m.write("{}.sol".format(k))
				# Make the previous solution infeasible
				addBinaryCut(k,m)
				k += 1
			else:
				searchBool = False
	print("Found {} optimal feasible Solutions!".format(k-1))
	m.write("knapsack.lp")

def main(): 
	# define data coefficients
	n = 9  #number of items
	p = [1, 6, 8, 9, 6, 7, 3, 2, 6]  #profits
	w = [1, 3, 6, 7, 5, 9, 4, 8, 5]  #weights
	v = [1, 3, 2, 9, 1, 4, 2, 4, 7]  #volumes
	wc = 1  #capacity (weight)
	vc = 1  #capacity (volume)
	m=CreateModel(n,p,w,v,wc,vc)
	SolveModel(m)
	  

if __name__ == '__main__':
   main()
