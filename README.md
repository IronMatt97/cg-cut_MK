# Multidimensional knapsack problem using Gomory Cuts' algorithm
### A simple CPLEX Python code for solving the Multidimensional knapsack problem
The problem is described below:
http://people.brunel.ac.uk/~mastjjb/jeb/orlib/mknapinfo.html

## Gomory Cuts algorithm
#todo
## Tests
The tests : 
http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/

*this code only supports the files mknap1.txt format

## Pre-requisites & Installing
- make sure you have IBM ILOG installed in your machine and the python interface for CPLEX.
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




 
