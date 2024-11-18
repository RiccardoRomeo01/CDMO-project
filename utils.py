import numpy as np
import json
import os

class Instance():
    def __init__(self, m, n, l, s, D):
        self.m = m
        self.n = n
        self.l = l
        self.s = s
        self.D = np.array(D)
        
    def get_values(self):
        return self.m, self.n, self.l, self.s, self.D


def load_instance(dir, instance_num):
    
    if instance_num < 10:
        instance_num = "0" + str(instance_num)
    
    dir +=  f"/inst{instance_num}.dat"
    
    file = open(dir, 'r')
    
    m = int(file.readline())
    n = int(file.readline())
    l = [int(x) for x in file.readline().split(" ") if x!= ""]
    s = [int(x) for x in file.readline().split(" ") if x!= ""]
    D = []
    for i in range(n+1):
        D.append([int(x) for x in file.readline().split(" ") if x!= "\n" if x!= ""])
    
    instance = Instance(m, n, l, s, D)
    
    return instance


def load_data_sat_mip(dir, instances_num):
    
    if type(instances_num) == int:
        
        if 0 < instances_num <= 21:
            return {str(instances_num): load_instance(dir, instances_num)}
        elif instances_num == 0:
            return {str(x): load_instance(dir, x) for x in range(1, 22)}
        else:
            raise ValueError("The instance ID is not acceptable")


    elif type(instances_num) == list:
        return {str(i): load_instance(dir, i) for i in instances_num}
    
    else:
        raise TypeError("The instance number should be an integer or a list of integer")

def read_instance_cp(path):
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

def load_data_cp(path, instance):
    """
    The function for each file in the path, it produces the instance
    """
    data = {}
    files = sorted(os.listdir(path))
    if instance == 0:
        for file in files:
            data[file] = (read_instance_cp(path + "/" + file))
    else:
        i = 0
        for file in files:
            if i == instance-1:
                data[file] = (read_instance_cp(path + "/" + file))
                break
            
            i += 1
    return data

def print_output(approach, time, optimal, obj, sol, instance_num, output_path):
    json_dict = {}

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
        "sol": sol
    }

    # Print of the solution on terminal
    print(f'{approach} = {json.dumps(json_dict[approach], indent=4)}')

    # Checking the existence of the output file
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Upload of the solution on the output file
    with open(file_path, 'w') as file:
        json.dump(json_dict, file, indent=4)