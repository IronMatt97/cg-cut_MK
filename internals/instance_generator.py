import random
import os

def generateInstances(num):
    print("A total of ",num," instances will be created.")
    for instance_num in range(0,num):
        instanceName="inst_"+str(instance_num)+".txt"
        print("\tGenerating instance called ",instanceName)
        instance = open("instances/"+instanceName, "w")

        #random.randint(5, 15)
        #TODO--
