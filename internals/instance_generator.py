from datetime import datetime
import random
import os

def generateInstance(instance_num : int, nvar : int , nconstraints : int, cluster_type : str):
    '''
    This function generate a cluster of istances with a specific number of var and number of contraints. 
    
    Arguments:
        num : number of istances to generate
        nvar : number of variables of the problem to generate
        nconstraints : number of the constraints of the problem to generate
    '''
    random.seed(getSeed())
    
    instanceName="inst_"+str(instance_num)+".txt"
    path_name="instances/"+cluster_type
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    instance = open(path_name+"/"+instanceName, "w")
    instance.write(str(nvar)+" "+str(nconstraints)+"\n")
    
    # Let's write the constraints 
    for constraint in range(0,nconstraints+1): # The +1 is for the objective function
        for var in range(0,nvar):
            n=random.randint(1,100)
            instance.write(" "+str(n))
        instance.write("\n")
    
    # Let's write the limits
    for constraint in range(0,nconstraints):
        n=random.randint(1,100*nvar)
        instance.write(" "+str(n))
    instance.close()

def getSeed():
    time = str(datetime.now())
    return time[len(time)-6:]

def generateClusterOfIstances(num_instances, var_range, constr_range,cluster_type) : 
    '''
    This function generate different clusters of istances.
    A cluster has a specific number of variables and number of contraints. 
    '''
    print("\tGenerating ",num_instances," for cluster type " , cluster_type,"...")
    for instance_num in range(0,num_instances):
        vars = random.randint(var_range[0], var_range[1])
        constr = random.randint(constr_range[0], constr_range[1])
        generateInstance(instance_num,vars,constr,cluster_type)
    print("\t...Done.")