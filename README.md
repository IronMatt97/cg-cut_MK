# Multidimensional knapsack problem using Gomory Cuts' algorithm
### A simple CPLEX Python code for solving the Multidimensional knapsack problem
The problem is described below:
http://people.brunel.ac.uk/~mastjjb/jeb/orlib/mknapinfo.html

## Gomory Cuts algorithm
The $i$-th row of the optimal tableau of the problem in standard form is expressed by :

$$x_{B_i} + \sum_j t_{ij}x_{N_j} = b^*_i$$

In this expression $x_{B_i}$ are the basic variables, $x_{N_j}$ are the non-basic variables and $t_{ij}$ is the multiplicative coefficient for non-basic variable $j$ in the $i$-th row.

A Gomory cutting plane (Gilmore and Gomory 1961) is expressed by : 

$$ \sum_j ( t_{ij} - \lfloor{t_{ij}}\rfloor) x_{N_j}  \geq {b^*_i} - \lfloor {b_i}  \rfloor $$

This is guaranteed to be a valid cut of the LP relaxation of an integer programming problem.

We use the Python implementation of CPLEX, to get the final tableau. We formulate the problem in standard form, with explicit slack variables, then we let CPLEX solve it and extract the final tableau, as well as the final right-hand-side vector $b^* = B^{-1} b$.

Finally, we count the number of possible cuts, leveraging the fact that one cut can be generated for each variable (whether it is a slack variable or not) that has a fractional value in the final solution.

We leverage the initial tableau, which contains a solution with only slack variables in the basis, in a useful configuration: row $i$ is of the form $c_{i1} x_1 + c_{i2} x_2 + s_i = b_i$.
In each cut, for each slack variable $s_k$, we take its coefficient $c_k$ in the Gomory cut and subtract the corresponding row of the initial tableau multiplied by $c_k$. Since the coefficient of the slack is 1 in each row, this will eliminate the slacks and result in a constraint expressed only in terms of $x_i, x_2$.
## Tests
The tests : 
http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/

*this code only supports the files mknap1.txt format.

### Generation of test
Inspired by the form of previous tests, we created a function that generates mknap problems randomly in .txt format. 


## Pre-requisites & Installing
- Make sure you have IBM ILOG installed in your machine and the python interface for CPLEX.
What is CPLEX: https://www.ibm.com/products/ilog-cplex-optimization-studio
Getting started: https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html

- Python3
- Clone this repository

## Running
In order to solve pseudo-randomically generated instances, we provide a config.ini file, in which it is possible to change generation parameters. After set the .ini file as desired, from the main root execute:
- In order to solve all possible instances:
```python main.py -all```
- In order to solve a single cluster of instances:
```python main.py -c cluster_type```
- In order to solve a single instance:
```python main.py -s instance_name.txt```

- It will generate files in solutions/[test_name] and lp/[test_name]
- All the resolution is readable in resolution.log

## Plots 
In order to plot the statistics : 
- Run  :
``` python /plots/stat_plotter.py ```
## References

Caprara, A., Fischetti, M. $\\{0,\frac{1}{2}\\}$-Chvátal-Gomory cuts. Mathematical Programming 74, 221–235 (1996). https://doi.org/10.1007/BF02592196

Authors
======================= 
- [Martina Salvati](https://github.com/msalvati1997)   (0292307)
- [Matteo Ferretti](https://github.com/IronMatt97)    (0300049)

