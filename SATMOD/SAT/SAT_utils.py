import math
from z3 import *
from itertools import combinations
import numpy as np

def necessary_bits(x):
    # This function computes the number of necessary bits in order to make a conversion integer to boolean representation
    return math.floor(math.log2(x)) + 1



def InttoBinary(num, length=None, dtype=bool):
    # Decodes an integer into its boolean representation
    num_bin = bin(num).split("b")[-1]
    if length:
        num_bin = "0" * (length - len(num_bin)) + num_bin
    num_bin = [dtype(int(s)) for s in num_bin]
    return num_bin


def BinarytoInt(model, bool_list):
    integers = []
    n = len(bool_list)
    for bit in range(n - 1, -1, -1):
        if model.evaluate(bool_list[bit]):
            integers.append(2**(n - bit -1))
    
    return Sum(integers)

def BinarytoInt2(bool_list):

    binary_string = ''.join('1' if b else '0' for b in bool_list)
    return int(binary_string, 2)


## Naive pairwise ##
def at_least_one_np(bool_vars, name=""):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name = ""):
    return And([Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)])

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one_np(bool_vars), at_most_one_np(bool_vars, name))

## Sequential encoding ##
def at_least_one_seq(bool_vars, name=""):
    return at_least_one_np(bool_vars)

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints)

def exactly_one_seq(bool_vars, name):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))


## Bit encoding ##
def toBinary_bw_auxiliary_func(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin

def at_least_one_bw(bool_vars, name=""):
    return at_least_one_np(bool_vars)

def at_most_one_bw(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary_bw_auxiliary_func(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name):
    return And(at_least_one_bw(bool_vars), at_most_one_bw(bool_vars, name))


## Heule encoding ##
def at_least_one_he(bool_vars, name=""):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars, name):
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name+"_")))

def exactly_one_he(bool_vars, name):
    return And(at_most_one_he(bool_vars, name), at_least_one_he(bool_vars))


## PseudoBoolean encoding ##
def exactly_one_pb(bool_vars, name=""):
    return PbEq([(v, 1) for v in bool_vars], 1)

def at_least_one_pb(bool_vars, name=""):
    return PbGe([(v, 1) for v in bool_vars], 1)
    
def at_most_one_pb(bool_vars, name=""):
    return PbLe([(v, 1) for v in bool_vars], 1)



## Naive pairwise k encoding ##
def at_least_k_np(bool_vars, k, name = ""):
    return at_most_k_np([Not(var) for var in bool_vars], len(bool_vars)-k, name)

def at_most_k_np(bool_vars, k, name = ""):
    return And([Or([Not(x) for x in X]) for X in combinations(bool_vars, k + 1)])

def exactly_k_np(bool_vars, k, name = ""):
    return And(at_most_k_np(bool_vars, k, name), at_least_k_np(bool_vars, k, name))


## Sequential k encoding ##
def at_least_k_seq(bool_vars, k, name=""):
    return at_most_k_seq([Not(var) for var in bool_vars], len(bool_vars)-k, name)

def at_most_k_seq(bool_vars, k, name):
    constraints = []
    n = len(bool_vars)
    s = [[Bool(f"s_{name}_{i}_{j}") for j in range(k)] for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0][0]))
    constraints += [Not(s[0][j]) for j in range(1, k)]
    for i in range(1, n-1):
        constraints.append(Or(Not(bool_vars[i]), s[i][0]))
        constraints.append(Or(Not(s[i-1][0]), s[i][0]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1][k-1])))
        for j in range(1, k):
            constraints.append(Or(Not(bool_vars[i]), Not(s[i-1][j-1]), s[i][j]))
            constraints.append(Or(Not(s[i-1][j]), s[i][j]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2][k-1])))   
    return And(constraints)

def exactly_k_seq(bool_vars, k, name):
    return And(at_most_k_seq(bool_vars, k, name), at_least_k_seq(bool_vars, k, name))


## Bit k encoding ##
def at_least_k_bw(bool_vars, k, name=""):
    return at_least_k_np(bool_vars, k)

def at_most_k_bw(bool_vars, k, name):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary_bw_auxiliary_func(i, m) for i in range(n)]

    for j in range(m):
        phi = Not(r[j])
        for i in range(n):
            if binaries[i][j] == "1":
                phi = Or(phi, r[j])
        constraints.append(Or(Not(bool_vars[i]), phi))

    for j in range(m):
        constraints.append(Or([Not(r[j]) for i in range(n) if binaries[i][j] == "1"]))

    return And(constraints)

def exactly_k_bw(bool_vars, k, name):
    return And(at_least_k_bw(bool_vars, k), at_most_k_bw(bool_vars, k, name))


## Heule k encoding ##
def at_least_k_he(bool_vars, k, name=""):
    return at_least_k_np(bool_vars, k)

def at_most_k_he(bool_vars, k, name):
    if len(bool_vars) <= 4:
        return And(at_most_k_np(bool_vars,k))
    y = Bool(f"y_{name}")
    return And(And(at_most_k_np(bool_vars[:3] + [y], k)), And(at_most_k_he(bool_vars[3:] + [Not(y)], k, name+"_")))

def exactly_k_he(bool_vars, k, name):
    return And(at_most_k_he(bool_vars, k, name), at_least_k_he(bool_vars, k))


## PseudoBoolean k encoding ##
def exactly_k_pb(bool_vars, k, name=""):
    return PbEq([(v, 1) for v in bool_vars], k)

def at_least_k_pb(bool_vars, k, name=""):
    return PbGe([(v, 1) for v in bool_vars], k)
    
def at_most_k_pb(bool_vars, k, name=""):
    return PbLe([(v, 1) for v in bool_vars], k)



def isEq(a, b):
    n = len(a)
    
    formulae = []
    for i in range(n-1, -1, -1):
        formulae.append(a[i] == b[i])
        
    f = And(formulae)
    return f



def isLessEq(a, b):
    constraints = []
    constraints.append(Or(Not(a[0]),b[0]))
    for i in range(1,len(a)):
        constraints.append(Implies(And([a[k] == b[k] for k in range(i)]), Or(Not(a[i]),b[i])))
    return And(constraints)



def sum_binary_numbers(a, b, d, label = ""):
    n = len(a)
    
    # we instantiate the carries
    c = [Bool(f"c_{label}_{i}") for i in range(n + 1)]
    
    
    formulae = []
    formulae.append(And(Not(c[0]), Not(c[n]))) # c_n = 0 and c_0 = 0
    # we need to make a reversed cycle
    for i in range(n-1, -1, -1):
        formulae.append(((a[i] == b[i]) == c[i+1]) == d[i])
        
        formulae.append((c[i] == (Or(And(a[i], b[i]),
                                    And(a[i], c[i+1]),
                                    And(b[i], c[i+1])))))
    f = And(formulae)
    
    return f



def sum_list_of_binary_numbers(l, result, label = ""):
    # number of binary representation we have to sum
    n = len(l) 
    
    # List of partial binary results
    p = [[Bool(f'partial_{label}_{i}_{bit}') for bit in range(len(l[0]))] for i in range(n-1)]
    
    formulae = []
    # If we have only one value we return the value itself
    if n == 1:
        formulae.append(isEq(l[0], result)) 
        f = And(formulae)
        return f
        
    # If we have only two values we return their summation
    if n == 2:
        formulae.append(sum_binary_numbers(l[0], l[1], result, label = label))
        f = And(formulae)
        return f
    
    if n >= 3:    
        # with more values we compute the summation on pairs
        formulae.append(sum_binary_numbers(l[0], l[1], p[0], label = label + "_partial_0"))
        for i in range(2, n-1):
            formulae.append(sum_binary_numbers(l[i], p[i-2], p[i-1], label = label +f"_partial_{i-1}"))
            
        formulae.append(sum_binary_numbers(l[-1], p[-2], result, label = label + f"_partial_{n-2}"))
        f = And(formulae)
    
    return f



def find_max_number(vec, maxi, label= ""):

    if len(vec) == 1:
        return isEq(vec[0], maxi)
    elif len(vec) == 2:
        constr1 = Implies(isLessEq(vec[0], vec[1]), isEq(vec[1], maxi))
        constr2 = Implies(Not(isLessEq(vec[0], vec[1])), isEq(vec[0], maxi))
        return And(constr1, constr2)
  
    par = [[Bool(f"maxpar_{label}_{i}_{b}") for b in range(len(maxi))] for i in range(len(vec)-2)]
    constr = []

    constr.append(Implies(isLessEq(vec[0], vec[1]), isEq(vec[1], par[0])))
    constr.append(Implies(Not(isLessEq(vec[0], vec[1])), isEq(vec[0], par[0])))

    for i in range(1, len(vec)-2):
        constr.append(Implies(isLessEq(vec[i+1], par[i-1]), isEq(par[i-1], par[i])))
        constr.append(Implies(Not(isLessEq(vec[i+1], par[i-1])), isEq(vec[i+1], par[i])))

    constr.append(Implies(isLessEq(vec[-1], par[-1]), isEq(par[-1], maxi)))
    constr.append(Implies(Not(isLessEq(vec[-1], par[-1])), isEq(vec[-1], maxi)))
    
    return And(constr)


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