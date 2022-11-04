from configparser import ConfigParser
from datetime import datetime
import logging
import random
import pandas as pd
import sys
import os
import math
import numpy as np
import shutil
from scipy.stats import pearsonr


logging.basicConfig(filename='resolution.log', format='%(asctime)s - %(message)s',level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

def getStatistics(name,cluster_type,nVar,nConstraints,optimal_sol,sol,sol_type,status,ncuts, elapsed_time, iterations):
    stats = []
    stats.append(name)
    stats.append(cluster_type)
    stats.append(nVar)
    stats.append(nConstraints)
    stats.append(optimal_sol)
    stats.append(sol)
    stats.append(sol_type)
    stats.append(status)
    stats.append(ncuts)
    stats.append(round(elapsed_time))
    stats.append(modulus(sol,optimal_sol))
    if optimal_sol==sol :
        stats.append(0)
    else :
        stats.append(modulus(sol,optimal_sol)/(optimal_sol+pow(10,-10)))
    stats.append(iterations)
    return stats

def modulus(x, y):
    if x >= y:
        result = x - y
    else:
        result = y - x
    return result

def generateIstances(cluster_type)  :
    columns = ["ratio_profits_weights","name"]
    # Read config file
    config = ConfigParser()
    config.read('config.ini')
    # Get a list of all Clusters 
    for cluster in config.sections():
        if cluster_type == cluster : 
            var_range=[int(config[cluster]['MIN_N_VAR']),int(config[cluster]['MAX_N_VAR'])]
            constr_range=[int(config[cluster]['MIN_COSTRAINTS']),int(config[cluster]['MAX_COSTRAINTS'])]
            num_instances=int(config[cluster]['NUM_ISTANCES'])
            df_list = generateClusterOfIstances(num_instances, var_range, constr_range, cluster)
            df = pd.DataFrame(df_list)
            df.columns = columns
            df.to_csv(cluster+'_ratio.csv',index=False)


def generateClusterOfIstances(num_instances, var_range, constr_range, cluster_type) : 
    '''
    This function generate different clusters of istances.
    A cluster has a specific number of variables and number of contraints.

    Arguments:
        num_instances : number of istances to generate
        var_range : the range between which a random number of variables will be created
        constr_range : the range between which a random number of constraints will be created
        cluster_type : the cluster type 
    '''
    print("\tGenerating ",num_instances,"instances for cluster type " , cluster_type,"...")
    df_list=[]
    for instance_num in range(0,num_instances):
        list = []
        vars = random.randint(var_range[0], var_range[1])
        constr = random.randint(constr_range[0], constr_range[1])
        corr,name = generateInstance(instance_num,vars,constr,cluster_type)
        list.append(corr)
        list.append(name)
        df_list.append(list)
    print("\t...Done.")
    return df_list

def generateInstance(instance_num : int, nvar : int , nconstraints : int, cluster_type : str):
    '''
    This function generate a cluster of istances with a specific number of var and number of contraints. 
    
    Arguments:
        instance_num : number of istances to generate
        nvar : number of variables of the problem to generate
        nconstraints : number of the constraints of the problem to generate
        cluster_type : the cluster type
    '''
    random.seed(getSeed())
    config = ConfigParser()
    config.read('config.ini')
    coefficients_range=[int(config[cluster_type]['MIN_COEFF_VAL']),int(config[cluster_type]['MAX_COEFF_VAL'])]
    instanceName="inst_"+str(instance_num)+".txt"
    path_name="instances/"+cluster_type
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    instance = open(path_name+"/"+instanceName, "w")
    instance.write(str(nvar)+" "+str(nconstraints)+"\n")
    profits=[]
    weights=[]
    correlations = []
    
    # Let's write the constraints 
    for constraint in range(0,nconstraints+1): # The +1 is for the objective function
        weights_i=[]
        for var in range(0,nvar):
            n=random.randint(coefficients_range[0],coefficients_range[1])
            instance.write(" "+str(n))
            if constraint==0 : #objective function
                profits.append(n)
            else : 
                weights_i.append(n)
        if not constraint==0 :
            weights.append(weights_i)
        instance.write("\n")

    mean_weights = []
    for p in range(0,len(profits)):  # prendo una variabile
        profit = profits[p] 
        sum_weights=0
        for w in weights :
           sum_weights += w[p]
        mean_weights.append(sum_weights/nconstraints)
    
    
    # Let's write the limits
    for constraint in range(0,nconstraints):
        n=random.randint(coefficients_range[0]*nvar,coefficients_range[1]*nvar)
        instance.write(" "+str(n))

    instance.close()
    assert(len(profits)==len(mean_weights))
    
    corr, _ = pearsonr(profits, mean_weights)


    return corr,instanceName.split(".txt")[0]

def getSeed():
    time = str(datetime.now())
    return time[len(time)-6:]

def flushLog(logName):
    '''
    This function flushes the log.
    '''
    with open(logName,'w') as file:
        pass 

    if os.path.exists("lp"):
        shutil.rmtree("lp")
    
    if os.path.exists("solutions"):
        shutil.rmtree("solutions")
            
 
    


def invalidInput():
    print("Invalid input.\nUsage:\n"
    +"A) Solve all clusters:\n\t--> python main.py -all\n"
    +"B) Solve a specific cluster (cluster_small, cluster_medium_A, cluster_medium_B, cluster_large):\n\t--> python main.py -c cluster_type\n"
    +"C) Solve a single problem instance:\n\t--> python main.py -s internals/cluster_type/instance_name.txt\n")
    sys.exit(-1)