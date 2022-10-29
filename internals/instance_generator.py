import random
import os

#TODO
def generateInstances(num : int, nvar : int , nconstraints : int):
    '''
    This function generate a cluster of istances with a specific number of var and number of contraints. 
    
    Arguments:
        num : number of istances to generate
        nvar : number of variables of the problem to generate
        nconstraints : number of the constraints of the problem to generate

    '''
    print("A total of ",num," instances will be created.")
    for instance_num in range(0,num):
        instanceName="inst_"+str(instance_num)+".txt"
        print("\tGenerating instance called ",instanceName)
        instance = open("instances/"+instanceName, "w")

        #random.randint(5, 15)

#TODO
def generateClustersOfIstances() : 
    '''
    This function generate different clusters of istances. ù
    A cluster has a specific number of variables and number of contraints. 
    '''



