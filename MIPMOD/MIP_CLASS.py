import time
import os
import json
from ortools.linear_solver import pywraplp
import numpy as np
from utils import Instance, load_data_sat_mip, print_output

class MIPSolver:
    SOLVERS = ['CBC', 'SCIP', 'HIGHS', 'GUROBI']
    
    def __init__(self, instance_number, data, output_dir="./res", timeout=300, model="CBC", symmetry_breaking=False):
        if model not in self.SOLVERS and model != "all":
            raise ValueError(f"Invalid solver '{model}'. Choose from {self.SOLVERS}.")
        
        self.instance_number = instance_number
        self.data = data
        self.output_dir = output_dir
        self.timeout = timeout
        self.solver_name = model
        self.symmetry_breaking = symmetry_breaking
        self.X = None
        self.T = None
        self.tot_dist = None
        self.Obj = None
        
    # define the variables to be used in the model
    def create_variables(self, model, m, n):
        # variable that is true if courier i travels from location j to location k, and false otherwise
        X = {(i, j, k): model.BoolVar(f'X[{i},{j},{k}]') for i in range(m) for j in range(n+1) for k in range(n+1)}
        
        # variable that represents the order in which courier i visits location j
        T = [model.IntVar(1, n, f'T[{k}]') for k in range(n)]
        
        # variable that represents the total distance traveled by courier i
        tot_dist = [model.IntVar(0, model.infinity(), f'tot_dist[{i}]') for i in range(m)]
        
        # variable that represents the maximum total distance traveled by any courier
        Obj = model.IntVar(0, model.infinity(), 'Obj')
        
        return X, T, tot_dist, Obj
    
    def set_constraints(self, model, m, n, X, T, tot_dist, Obj, li, sj, D):
        # Constraints code with symmetry breaking condition applied if enabled
        for i in range(m):
            model.Add(Obj >= tot_dist[i])
        
        for k in range(n):
            model.Add(sum(X[(i, j, k)] for i in range(m) for j in range(n+1)) == 1)  
            model.Add(sum(X[(i, k, j)] for i in range(m) for j in range(n+1)) == 1)  
        
        for i in range(m):
            model.Add(sum(X[(i, j, n)] for j in range(n)) == 1)  
            model.Add(sum(X[(i, n, j)] for j in range(n)) == 1)  
        
        for i in range(m):
            for j in range(n):
                model.Add(X[(i, j, j)] == 0)
        
        for i in range(m):
            for j in range(n):
                model.Add(sum(X[(i, k, j)] for k in range(n+1)) == sum(X[(i, j, k)] for k in range(n+1)))
        
        for i in range(m):
            model.Add(sum(X[(i, j, k)] * sj[k] for j in range(n+1) for k in range(n)) <= li[i])
            
        avg_items = n // m
        delta = 2
        gamma = 1
        max_items = avg_items + delta
        min_items = max(0, avg_items - gamma)
        
        for i in range(m):
            model.Add(sum(X[(i, j, k)] for j in range(n) for k in range(n+1)) <= max_items)
            model.Add(sum(X[(i, j, k)] for j in range(n) for k in range(n+1)) >= min_items)

        bigM = 2 * n
        for i in range(m):
            for k in range(n):
                model.Add(T[k] <= 1 + bigM * (1 - X[(i, n, k)]))  
            for j in range(n):
                for k in range(n):
                    model.Add(T[j] >= T[k] + 1 - (bigM * (1 - X[(i, k, j)])))
                    model.Add(T[j] <= T[k] + 1 + (bigM * (1 - X[(i, k, j)])))  
        
        for i in range(m):
            model.Add(tot_dist[i] == sum(X[(i, j, k)] * D[j][k] for j in range(n+1) for k in range(n+1)))
        
        if self.symmetry_breaking:
            for i in range(m - 1):
                model.Add(tot_dist[i] <= tot_dist[i + 1])

    def solve(self):
        # Define instance numbers to run: all if 0, otherwise only the specified instance
        instance_numbers = list(self.data.keys()) if self.instance_number == 0 else [str(self.instance_number)]
        solvers_to_use = self.SOLVERS if self.solver_name == "all" else [self.solver_name]
        
        for instance_num in instance_numbers:

            instance_data = self.data[instance_num]
            m, n, li, sj, D = instance_data.get_values()

            for solver_name in solvers_to_use:

                # Restrict `CBC` and `HIGHS` to instances 0-10 if all instances are selected
                if int(instance_num) > 10 and (solver_name == "CBC" or solver_name == "HIGHS"):
                    print(f"Skipping solver {solver_name} for instance {instance_num} due to instance limit.")
                    continue

                model = pywraplp.Solver.CreateSolver(solver_name)
                if not model:
                    print(f"Solver {solver_name} is not available, skipping.")
                    continue

                # Initialize variables, constraints, and objective
                self.X, self.T, self.tot_dist, self.Obj = self.create_variables(model, m, n)
                model.Minimize(self.Obj)
                self.set_constraints(model, m, n, self.X, self.T, self.tot_dist, self.Obj, li, sj, D)
                model.set_time_limit(self.timeout * 1000)

                # Solve and measure time
                start_time = time.time()
                status = model.Solve()
                elapsed_time = int(time.time() - start_time)

                # Prepare result structure
                result = {
                    'time': min(self.timeout, elapsed_time),
                    'optimal': status == pywraplp.Solver.OPTIMAL,
                    'obj': int(round(self.Obj.solution_value(), 0)) if status != pywraplp.Solver.INFEASIBLE else None,
                    'sol': self.extract_solution(status, m, n)
                }

                # Output result if feasible solution was found
                if result['sol']:
                    print_output(
                        approach=f"{solver_name}{'_sb' if self.symmetry_breaking == 'sb' else ''}",
                        time=result['time'],
                        optimal=result['optimal'],
                        obj=result['obj'],
                        sol=result['sol'],
                        instance_num=instance_num,
                        output_path=self.output_dir + "/MIP/"
                    )
                else:
                    print(f"No solution found for instance {instance_num} with solver {solver_name}.")

        return result


    def extract_solution(self, status, m, n):
        """Helper function to extract solution if feasible."""
        if status not in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}:
            return None

        solution = [[] for _ in range(m)]
        for i in range(m):
            current_node = n
            while True:
                next_node = None
                for j in range(n + 1):
                    if self.X[(i, current_node, j)].solution_value() > 0.5:
                        next_node = j
                        break
                if next_node is None or next_node == n:
                    break
                solution[i].append(next_node + 1)
                current_node = next_node
        return solution



