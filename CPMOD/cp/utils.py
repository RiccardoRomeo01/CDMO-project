import os
import json
import numpy as np
# from pulp import *


def read_instance(path):
    """
    The function takes in input a txt files and return a tuple of the problem's instance
    """
    # Read the instance file from the general txt type
    f = open(path, 'r')
    lines = f.readlines()
    distances = []
    for i, line in enumerate(lines):
        if i == 0:
            n_couriers = int(line)
        elif i == 1:
            n_items = int(line)
        elif i == 2:
            couriers_size = [int(e) for e in line.split(' ') if e != '\n' and e != '']
        elif i == 3:
            objects_size = [int(e) for e in line.split(' ') if e != '\n' and e != '']
        else:
            distances.append([int(e) for e in line.split(' ') if e != '\n' and e != ''])
    f.close()

    return n_couriers, n_items, couriers_size, objects_size, distances


def load_data(path, instance):
    """
    The function for each file in the path, it produces the instance
    """
    data = {}
    files = sorted(os.listdir(path))
    if instance == 0:
        for file in files:
            data[file] = (read_instance(path + "/" + file))
    else:
        i = 0
        for file in files:
            if i == instance:
                break
            data[file] = (read_instance(path + "/" + file))
            i += 1
    return data

def saving_file(json_dict, path, filename):

    filename = str(int(filename.split(".")[0]))
    if not os.path.exists(path):
        os.makedirs(path)
    
    with open(path + filename + ".json", 'w') as file:
        json.dump(json_dict, file, indent=4)



def print_sat(asg):
    for k in range(len(asg)):
        print("Courier = ", k)
        for i in range(len(asg[k])):
            print(asg[k][i])

def get_dict(seconds, optimal, obj, res):
    return {
            'time': seconds,
            'optimal': optimal,
            'obj': obj,
            'sol': res
        }




def creating_path(instance,num_items):
    """
    Function use to create the list of items for each courier which will be used by the json dict,
    In particular taken the dict {start:end} in return the list in the correct order.
    Ex input {1:5,4:6,5:4,6:1} where 6 in num_items, the function will return a list
    [1,5,4], this list will used to write it in the json dict
    """
    if instance == {}:
        return []
    elem = instance[num_items]
    items_for_courier = [elem + 1]
    while elem != num_items:
        elem = instance[elem]
        items_for_courier.append(elem + 1)
    return items_for_courier[:-1]


def format_output_smtlib(result, num_items, time, opt):
    obj = int(result[0])
    time = int(time)
    all_dist = []
    for i in range(1, len(result)):
        all_dist.append(creating_path(result[i], num_items))

    return get_dict(time, opt,obj,all_dist)



def sorting_couriers(value):
    courier_size = value[2]
    size_pos = {}
    # Initialization
    for i in range(len(courier_size)):
        size_pos[courier_size[i]] = []

    for i in range(len(courier_size)):
        size_pos[courier_size[i]].append(i)

    courier_size_copy = courier_size.copy()
    courier_size_copy.sort(reverse=True)
    corresponding_dict = {}
    for i in range(len(courier_size)):
        corresponding_dict[i] = size_pos[courier_size_copy[i]][0]
        size_pos[courier_size_copy[i]].pop(0)

    return corresponding_dict

def sorting_correspondence(res, corresponding_dict):
    '''
    :param res: list of variables returned by a certain model
    :param corresponding_dict: dictionary where the keys are the couriers 
                               couriers in order and the values are the 
                               corresponding couriers before the sorting

    :result: the set of result reordered according to the original instance
    '''

    

    # We reorder only the result whose first dimension is M 
    if not isinstance(res, list):
        return res
    
    if len(res) != len(corresponding_dict):
        return res

    final_res = [[] for _ in range(len(res))]
    # Assigned the corrispondences with the dictionary
    for i in range(len(res)):
        courier = corresponding_dict[i]
        final_res[courier] = res[i]
    return final_res

def set_lower_bound(distances, all_travel):
    """
    :param distances: matrix of distances
    :result lb: the lower bound for the objective funciton
    :result dist_lb: the lower bound for the array of courier distances
    """
    last_row = distances[-1]
    last_column = [distances[i][-1] for i in range(len(distances[0]))]
    value1 = last_column[np.argmax(last_row)] + max(last_row)
    value2 = last_row[np.argmax(last_column)] + max(last_column)
    lb = max(value1, value2)

    if not all_travel:
        dist_lb = 0
    else:
        value1 = last_column[np.argmin(last_row)] + min(last_row)
        value2 = last_row[np.argmin(last_column)] + min(last_column)
        dist_lb = min(value1, value2) 

        

    return (lb, dist_lb)

def set_upper_bound(distances, all_travel, couriers):
    '''
    :param distances: matrix of distances
    :param all_travel: boolean true if max(items_size) <= min(courier_size)

    return the two possible upper bounds
    '''
    items = len(distances) - 1
    if not all_travel:
        return sum([max(distances[i]) for i in range(items+1)])
    else:
        dist_np = np.array(distances)
        dist_sorted = dist_np[np.max(dist_np, axis=0).argsort()]
        max_long_path = sum([max(dist_sorted[i]) for i in range(couriers-1, items+1)])

        return int(max_long_path)
