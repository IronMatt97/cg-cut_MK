import random
import os

#TODO
def generateStatistics():
    '''
    This function generate statistics of Solved Clusters. 
    '''

#TODO
def saveToCSV() : 
    '''
    This function save to CSV info about istance solution.
    '''

def getStatistics(name,cluster_type,nVar,nConstraints,optimal_sol,sol,sol_type,status,ncuts, elapsed_time):
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
    stats.append(elapsed_time)
    if optimal_sol==sol :
        stats.append(0) #0 gap
    else : 
        gap = sol-optimal_sol
        stats.append(gap)
    return stats