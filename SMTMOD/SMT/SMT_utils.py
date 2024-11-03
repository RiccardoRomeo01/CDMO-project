from itertools import combinations
from pysmt.shortcuts import Symbol, And, Or, Not
from pysmt.typing import BOOL
import numpy as np


# NAIVE PAIRWISE ENCODING
def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name = ""):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)])

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one_np(bool_vars), at_most_one_np(bool_vars, name))


# HEULE ENCODING
def at_least_one_he(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars, name):
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Symbol(f"y_{name}", BOOL)
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name+"_")))

def exactly_one_he(bool_vars, name):
    return And(at_most_one_he(bool_vars, name), at_least_one_he(bool_vars))



def set_lower_bound(D):
    # If the courier must carry at least one item then we use as lower bound the longest distance base ->item -> base
    last_row = D[-1]
    last_column = D[:,-1]
    value1 = last_column[np.argmax(last_row)] + max(last_row)
    value2 = last_row[np.argmax(last_column)] + max(last_column)
    lb = max(value1, value2)
    return lb 

def set_upper_bound(D, n):
    # As upper bound we use the maximum distance that one courier would travel if he carries all items
    ub = D[n,0] + np.sum(D[0: n-1, 1: n].diagonal()) + D[n-1, n]    
    return ub