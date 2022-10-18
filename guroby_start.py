#!/usr/bin/env python3
import sys
import gurobipy as gp
from gurobipy import GRB
import pandas as pd


def addBinaryCut(j):
	B, NB = [], []
	for i in range(n):
		B.append(i) if (x[i].x == 1) else NB.append(i)
	# Add binary cut to Model
	m.addConstr((gp.quicksum(x[i] for i in B) - gp.quicksum(x[j] for j in NB)) <= len(B) - 1, name="binaryCut{}".format(j))
	m.update()

def availability_constraint(model, i):
    
    return sum(model.x[i, k] for k in model.K) <= model.b[i]

def weight_constraint(model, k):
    
    return sum(model.x[i, k] * model.w[i] for i in model.I) <= model.kw[k]

def volume_constraint(model, k):
    
    return sum(model.x[i, k] * model.v[i] for i in model.I) <= model.kv[k]

def obj_function(model):
    
    return - sum(model.x[i, k] * model.c[i]\
        for i in model.I for k in model.K)

# define data coefficients
n = 9
p = [1, 6, 8, 9, 12, 25, 3, 12, 6]
w = [1, 3, 6, 7, 5, 9, 4, 8, 5]
c = 1



# Maximize
#   6 x[0] + 6 x[1] + 8 x[2] + 9 x[3] + 6 x[4] + 7 x[5] + 3 x[6] + 2 x[7] + 6 x[8]
# Subject To
#  2 x[0] + 3 x[1] + 6 x[2] + 7 x[3] + 5 x[4] + 9 x[5] + 4 x[6] + 8 x[7] + 5 x[8] <= 20


# create empty model
m = gp.Model()

# add decision variables
x = m.addVars(n, vtype=GRB.BINARY, name='x')

# set objective function
m.setObjective(gp.quicksum(p[i] * x[i] for i in range(n)), GRB.MAXIMIZE)

# add constraint
m.addConstr((gp.quicksum(w[i] * x[i] for i in range(n)) <= c), name="knapsack")

# Add Lazy Constraints
m.update()

# quiet gurobi
m.setParam(GRB.Param.LogToConsole, 0)

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
			addBinaryCut(k)
			k += 1
		else:
			searchBool = False

print("Found {} optimal feasible Solutions!".format(k))

m.write("knapsack.lp")