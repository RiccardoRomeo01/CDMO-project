from itertools import combinations
from pysmt.shortcuts import Symbol, And, Or, Not
from pysmt.typing import BOOL
from pysmt.fnode import FNode
import numpy as np
import os
import json


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



def at_least_k_np(bool_vars, k, name = ""):
    return at_most_k_np([Not(var) for var in bool_vars], len(bool_vars)-k, name)

def at_most_k_np(bool_vars, k, name = ""):
    return And([Or([Not(x) for x in X]) for X in combinations(bool_vars, k + 1)])



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


def serialize_SMT_solution(sol):
    serialized_sol = []
    for el in sol:
        path = []
        for e in el:
            path.append(int(e.serialize()))
        serialized_sol.append(path)
    
    return serialized_sol


def from_dict_to_list(dictionary):
    m = len(dictionary)
    solution = [[] for _ in range(m)]

    for key, value in dictionary.items():
        solution[key] = value

    return solution


def print_output_SMT(approach, time, optimal, obj, sol, instance_num, output_path):
    json_dict = {}

    serialized_sol = serialize_SMT_solution(sol=sol)

    # Checking if the file exists and loading data on it
    filename = f"{instance_num}.json"
    file_path = os.path.join(output_path, filename)

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            json_dict = json.load(file)

    # Adding new values to the dictionary
    if approach not in json_dict:
        json_dict[approach] = []

    json_dict[approach] = {
        "time": time,
        "optimal": optimal,
        "obj": obj,
        "sol": serialized_sol
    }

    # Print of the solution on terminal
    print(f'{approach} = {json.dumps(json_dict[approach], indent=4)}')

    # Checking the existence of the output file
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Upload of the solution on the output file
    with open(file_path, 'w') as file:
        json.dump(json_dict, file, indent=4)