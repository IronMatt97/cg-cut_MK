import random
import os


def getStatistics(name,cluster_type,nVar,nConstraints,optimal_sol,sol,sol_type,status,ncuts, elapsed_time, iterations, low, upper):
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
    stats.append(iterations)
    stats.append(low)
    stats.append(upper)
    return stats