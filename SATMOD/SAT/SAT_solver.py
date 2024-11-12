from z3 import *
from utils import *
from SATMOD.SAT.SAT_utils import *
import time as t
from SATMOD.SAT.SAT_constants import *

class SATsolver:
    def __init__(self, input_data, output_path, strategy, timeout=300, encoding="np", symmetry_breaking="False", fair_division="no_fair"):
        self.input_data = input_data
        self.timeout = timeout
        self.encoding = encoding
        self.solver = Solver()
        self.output_path = output_path
        self.strategy = strategy
        self.symmetry_breaking = symmetry_breaking
        self.fair_division = fair_division
        
    def set_solver(self, strat, enc):
        self.solver = Solver()
        self.solver.set('timeout', self.timeout * 1000)
        
        self.strategy = strat
        self.encoding = enc
        
        
    def solve(self):
        general_all_calling_flag = 0
        
        if self.strategy == "all" and self.encoding == "all" and self.symmetry_breaking == "all" and self.fair_division == "all":
            general_all_calling_flag = 1 # a flag used to understand how the script was called
            # for each instance
            for num, instance in self.input_data.items():
                    print(f"\n===== OUTPUT FOR INSTANCE {num} =====")
                    # for each strategy
                    for strat in STRATEGIES:
                        # for each encoding
                        for enc in ENCODINGS:
                            # with and without simmetry breaking
                            for sim in SYMMETRY:
                                # with and without fair load division among couriers
                                for f in FAIR_DIVISION:
                                
                                    approach = strat + " " + enc + " " + sim + " " + f
                                    
                                    # The SAT solver is able to encode only the first 10 instances
                                    if int(num) >= 0 and int(num) <= 10:
                                        # we set the simmetry flag
                                        self.symmetry_breaking = sim
                                            
                                        # we set the fair load division flag
                                        self.fair_division = f
                                            
                                        # setting the solver
                                        # print(f"The approach is: {approach}")
                                            
                                        self.set_solver(strat, enc)
                                            
                                        # setting the constraints
                                        obj_function, x, current_loads, total_current_load, current_distances, total_current_distance = self.set_constraints(instance)
                                            
                                        # we search the optimal solution using the appriate search strategy
                                        if self.strategy == "linear":
                                            time, optimal, obj, sol = self.search_optimal_linear(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                                        elif self.strategy == "binary":
                                            time, optimal, obj, sol = self.search_optimal_binary(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                                            
                                        # we print the output for that instance
                                        print_output(approach, time, optimal, obj, sol, num, self.output_path + "/SAT/")
                                            
                                    # Here we manage the special case of instance 16
                                    elif int(num) == 16 and self.strategy == "binary" and self.encoding != "seq" and self.fair_division == "fair":
                                        
                                        self.set_solver(self.strategy, self.encoding)
                                        
                                        obj_function, x, current_loads, total_current_load, current_distances, total_current_distance = self.set_constraints(instance)
                                        
                                        time, optimal, obj, sol = self.search_optimal_binary(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                                        
                                        print_output(approach, time, optimal, obj, sol, num, self.output_path + "/SAT/")
                                        
                                    else:
                                        # we print an empty dictionary
                                        print_output(approach, self.timeout, False, "N/A unknown", "N/A unknown", num, self.output_path + "/SAT/")
                    print()
                    
            print()
        
        
        
        if general_all_calling_flag == 0:
            
            approach = self.strategy + " " + self.encoding + " " + self.symmetry_breaking + " " + self.fair_division
            
            for num, instance in self.input_data.items():
                
                print(f"\n===== OUTPUT FOR INSTANCE {num} =====")
                output_dict = {}
                if int(num) >= 0 and int(num) <= 10:
                   
                    # setting the solver
                    self.set_solver(self.strategy, self.encoding)

                    # setting constraints
                    obj_function, x, current_loads, total_current_load, current_distances, total_current_distance = self.set_constraints(instance)
                        
                    # seraching optimal solution
                    if self.strategy == "linear":
                        time, optimal, obj, sol = self.search_optimal_linear(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                    elif self.strategy == "binary":
                        time, optimal, obj, sol = self.search_optimal_binary(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                        
                    # printing the output for that instance
                    print_output(approach, time, optimal, obj, sol, num, self.output_path + "/SAT/")
                
                # Here we manage the special case of instance 16
                elif int(num) == 16 and self.strategy == "binary" and self.encoding != "seq" and self.fair_division == "fair":
                    
                    self.set_solver(self.strategy, self.encoding)
                    
                    obj_function, x, current_loads, total_current_load, current_distances, total_current_distance = self.set_constraints(instance)
                    
                    time, optimal, obj, sol = self.search_optimal_binary(num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance)
                    
                    print_output(approach, time, optimal, obj, sol, num, self.output_path + "/SAT/")
                else:
                    print_output(approach, self.timeout, False, "N/A unknown", "N/A unknown", num, self.output_path + "/SAT/")
                print()
            print()
    
    
    def set_encodings(self):
        
        if self.encoding == "np":
            at_most_one = at_most_one_np
            at_least_one = at_least_one_np
            exactly_one = exactly_one_np
            at_least_k = at_least_k_np
        elif self.encoding == "seq":
            at_most_one = at_most_one_seq
            at_least_one = at_least_one_seq
            exactly_one = exactly_one_seq
            at_least_k = at_least_k_seq
        elif self.encoding == "bw":
            at_most_one = at_most_one_bw
            at_least_one = at_least_one_bw
            exactly_one = exactly_one_bw
            at_least_k = at_least_k_bw
        elif self.encoding == "he":
            at_most_one = at_most_one_he
            at_least_one = at_least_one_he
            exactly_one = exactly_one_he
            at_least_k = at_least_k_he
        elif self.encoding == "pb":
            at_most_one = at_most_one_pb
            at_least_one = at_least_one_pb
            exactly_one = exactly_one_pb
            at_least_k = at_least_k_pb
        
        return at_most_one, at_least_one, exactly_one, at_least_k
    
    
    
    def set_constraints(self, instance):
        
        # First of all we set the encoding to use
        at_most_one, at_least_one, exactly_one, at_least_k = self.set_encodings()
        
        
        m, n, l, s, D = instance.get_values()
        maximum_load = necessary_bits(sum(l))
        maximum_distance = necessary_bits(set_upper_bound(D, n))
        number_of_bits = max(maximum_load, maximum_distance) + 1
        print(f"The number of bits is: {number_of_bits}")
        
        # Binary representations
        l = [[BoolVal(b) for b in InttoBinary(l[i], length = number_of_bits)] for i in range(m)] # couriers loads
        s = [[BoolVal(b) for b in InttoBinary(s[j], length = number_of_bits)] for j in range(n)] # item sizes
        D = [[[BoolVal(b) for b in InttoBinary(D[i][j], length = number_of_bits)] for j in range(n+1)] for i in range(n+1)] # distances matrix
        
        
        
        # VARIABLES
        # xijk = True if the courier i carries the item j during the step k (I have in total n+2 steps: n + start_point + end_point)
        # xijk = True if the courier i is in position j during the step k
            #  0 <= i <= m-1
            #  0 <= j <= n
            #  0 <= k <= n+1
        if self.fair_division == "no_fair":
            k_upper_bound = n
            
        if self.fair_division == "fair":
            print("I'm applying fair load division among couriers")
            fair_division_coefficient = n // m
            k_upper_bound = fair_division_coefficient + K_BOUNDARY_CONSTANT
            print(f"Each courier has to bring at least {fair_division_coefficient} items")
        
        
        x = [[[Bool(f"x_{i}_{j}_{k}") for k in range(k_upper_bound + 2)] for j in range(n + 1)] for i in range(m)]
        
        
        # Each item can be picked up only once and all the items must be picked up
        for j in range(1,n+1):
            self.solver.add(exactly_one([x[i][j][k] for i in range(m) for k in range(k_upper_bound+2)], f"all_elements_{j}"))


        # Each courier must start its tour in base
        for i in range(m):
            # This means that at the moment 0 the courier is in position 0 (base)
            self.solver.add(x[i][0][0] == True)


        # If the courier at the moment k is in base then he will be in base also for each moment forward (with k>=1)
        for i in range(m):
            for k in range(1, k_upper_bound+1):
                self.solver.add(Implies(x[i][0][k], x[i][0][k+1]))
        
        # In each moment the courier must be at least in one position and cannot have the ubiquity gift (must be in at mosto one posotion)
        for i in range(m):
            for k in range(k_upper_bound+2):
                self.solver.add(exactly_one([x[i][j][k] for j in range(n+1)], f"only_in_one_pos_{i}_{k}"))


        # Each courier has to return in base in some moment after the start of the tour
        for i in range(m):
            # Each courier must return in base in one moment 1<=k<=n+1
            self.solver.add(at_least_one([x[i][0][k] for k in range(1, k_upper_bound+2)], f"return_to_depot_{i}"))

        
        ### NO FAIR LOAD DIVISION CONSTRAINT ###
        if self.fair_division == "no_fair":
            # Each courier must visit at least one position which is not the depot, this because n>=m
            for i in range(m):
                self.solver.add(at_least_one([x[i][j][k] for j in range(1, n+1) for k in range(k_upper_bound+2)], f"start_{i}"))    
            
        ### FAIR LOAD DIVISION CONSTRAINT ###
        if self.fair_division == "fair":
            # Se impose that each courier must bring at least n//m items, in other words it has to visit at least n//m positions
            for i in range(m):
                self.solver.add(at_least_k([x[i][j][k] for j in range(1, n+1) for k in range(k_upper_bound+2)], fair_division_coefficient, f"fair_{i}"))
            
        
         
                
        # EACH COURIER CANNOT BRING MORE THAN HIS MAXIMUM LOAD,
        # current_loads[i][j] contains the j-th size carried by the i-th courier
        # total_current_load[i] contains the total size carried by the i-th courier
        current_loads = [[[Bool(f"cl_{i}_{j}_{bit}") for bit in range(number_of_bits)] for j in range(n)] for i in range(m)]
        total_current_load = [[Bool(f"tcl_{i}_{bit}") for bit in range(number_of_bits)] for i in range(m)]

        # If the courier i, at a time k is carring the item j then we copy its weight into current_loads[i]
        for i in range(m):
                    
            for j in range(n):
                # If at least one is True then we copy all the bits
                self.solver.add(Implies(at_least_one( [x[i][j+1][k] for k in range(1, k_upper_bound + 2)] ), # range(1, k_upper_bound + 1)
                                    isEq(current_loads[i][j], s[j])
                                    ))
                # Otherwise we copy only zeros: Not(current_loads[i][j][bit])
                self.solver.add(Implies(Not(at_least_one([x[i][j+1][k] for k in range(1, k_upper_bound + 2)])), # range(1, k_upper_bound + 1)
                                    And([Not(current_loads[i][j][bit]) for bit in range(number_of_bits)])
                                    ))
                                
            # Now, for each courier we sum all the sized carried by the courier
            self.solver.add(sum_list_of_binary_numbers(l = current_loads[i], result = total_current_load[i], label = f"loads_of_{i}"))
            # We impose the total load carried by a courrier to be less or equal to the load that this courier can carry
            self.solver.add(isLessEq(total_current_load[i], l[i]))  
        
        
        ### SYMMETRY BREAKING CONSTRAINT ### 
        if self.symmetry_breaking == "sb":
            # '''
            # If the carriable load of two couriers is the same then we impose one of them to carry more load respect to the other
            for i1 in range(m):
                for i2 in range(i1 + 1, m):
                    # the constraint must be applied to two different couriers
                    if i1 != i2:
                        self.solver.add(Implies(isEq(l[i1], l[i2]), 
                                        isLessEq(total_current_load[i2], total_current_load[i1])
                                        ))                   
            # '''
        
        
        # we define the objective function (in this moment it is empty)
        obj_function = [Bool(f"obj_{bit}") for bit in range(number_of_bits)]
        #### DISTANCES ####
        # current_distances[i][j] contains the j-th distance traveled by the i-th courier
        # total_current_distance[i] contains the total distance traveled by the i-th courier
        current_distances = [[[Bool(f"cd_{i}_{j}_{bit}") for bit in range(number_of_bits)] for j in range(n + 1)] for i in range(m)]
        total_current_distance = [[Bool(f"tcd_{i}_{bit}") for bit in range(number_of_bits)] for i in range(m)]
        # we impose those constraints for each courier
        for i in range(m):
            
            # We copy the start of the tour, copying the traveled distance between the moment k=0 and the moment k=1
            for j in range(1, n+1): # We control all the positions from j=1 to j=n, in other words we search when the courier is NOT in base
                # If x[i][j][1] is True this means that the courier at time k = 1 is in position j. Then we copy the traveled distance D_n_j in current_distances
                self.solver.add(Implies(x[i][j][1], isEq(current_distances[i][j], D[n][j-1])))
            
            
            # We check the position of the courier in k and in k+1 and copy the distance between the two positions in current_distances[i][j]
            # For each moment 1 <= k <= n + 1 we check where the courier is for k and k+1
            for k in range(1, k_upper_bound + 1):
                # For each pair of possible objects we check whether the two objects j1 and j2 are brought by the courier
                # So we check the courier's position in two consecutive moments
                for j1 in range(1, n + 1):
                    for j2 in range(1, n + 1):
                        # If x[i][j1][k] = True and x[i][j2][k+1] = True then we copy the distance D_j1_j2 in current_distances
                        self.solver.add(Implies(And(x[i][j1][k], x[i][j2][k+1]), isEq(current_distances[i][j2], D[j1-1][j2-1])))
                        
                    # We check if the courier is returning to base after being at position j1
                    # In current_distances[i][0] is the distance traveled by the courier to return home
                    self.solver.add(Implies(And(x[i][j1][k], x[i][0][k+1]), isEq(current_distances[i][0], D[j1-1][n])))
            
                
            # WARNING: many distances are undefined, so I have to define a value for them. To do this I do the following:
            # for each object I check whether the courier took it at any time, if not I set the j-th distance equal to zero
            # The courier is not necessarily always on the move at every moment k. Could finish the tour in fewer steps. 
            # So for all the other steps I have to copy a zero distance into current_distances[i]
            for j in range(1, n+1):
                self.solver.add(Implies(Not(at_least_one([x[i][j][k] for k in range(k_upper_bound+2)])), isEq(current_distances[i][j], D[0][0])))
            
            # We compute the total amount traveled by each courier and put it in total_current_distance
            self.solver.add(sum_list_of_binary_numbers(l = current_distances[i], result = total_current_distance[i], label = f"distance_of_{i}"))
        
        
        # we impose the constraints for the optimizing methods (linear and binary)
        self.solver.add(find_max_number(total_current_distance, obj_function))    

        # binary search case
        if self.strategy == "binary":
            self.solver.push()
        
        
        return obj_function, x, current_loads, total_current_load, current_distances, total_current_distance



    def search_optimal_linear(self, num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance):
        
        m, n, l, s, D = instance.get_values()
        maximum_load = necessary_bits(sum(l))
        maximum_distance = necessary_bits(set_upper_bound(D, n))
        number_of_bits = max(maximum_load, maximum_distance) + 1
        
        if self.fair_division == "no_fair":
            k_upper_bound = n
        if self.fair_division == "fair":
            k_upper_bound = n // m + K_BOUNDARY_CONSTANT
        
        previousModel = None
        is_sat = True
        is_optimal = True
        
        
        # Start of the counter
        start_time = t.time()
        # This is a flag used to indicate the i-th found solution
        solution_number = 0
        
        # We save the solver status in order to add later new conditions
        self.solver.push()
        
        while(is_sat):
            # We check the solver status
            status = self.solver.check()
            
            if status == sat:
                # We increment the solution counter because if it is sat it means we have found another solution
                solution_number = solution_number + 1 
                print(f"Solution number: {solution_number}, status: {status}")
                print()
                
                # we save this model as previousModel
                model = self.solver.model()
                previousModel = model
                
                # we check the time used in order to find the last solution
                current_time = t.time()
                passed_time = int((current_time - start_time))
                self.solver.set('timeout', (self.timeout - passed_time)*1000)
                
                # we save the objective function of the previous model
                previous_obj_function = [model.evaluate(obj_function[bit]) for bit in range(number_of_bits)]
                
                
                # Now we impose the solver to find a solution which must be smaller than the previous one
                self.solver.add(Not(isLessEq(previous_obj_function, obj_function)))
            
            # If the status is unsat we stop the cycle or we return an empty output (unsat problem)   
            elif status == unsat:
                if solution_number == 0:
                    print("UNSAT")
                    current_time = t.time()
                    passed_time = int((current_time - start_time))
                    return passed_time, False, "N/A unsat", []
            
                is_sat = False
            
            # If the status is unknown it means that the time exceeded and we return an empty output
            elif status == unknown:
                if solution_number == 0:
                    print("TIME EXCEEDED")
                    return self.timeout, False, "N/A unknown", []
                
                is_sat = False
                is_optimal = False
            
            
        # We compute the requested time
        current_time = t.time()
        passed_time = current_time - start_time
            
        # We take the last model
        model = previousModel

        # We take from the last model all the distances and the objective function
        total_current_distance_copy = [[model.evaluate(total_current_distance[i][b]) for b in range(number_of_bits)] for i in range(m)]
        distances = [BinarytoInt2(np.array(total_current_distance_copy[i])) for i in range(m)]
        obj_function_integer = max(distances) 

        # We take all the visited locations by each courier    
        visited_locations = [[] for _ in range(m)]
        for i in range(m):            
            for k in range(k_upper_bound + 2):
                for j in range(1, n + 1):
                    if is_true(model.evaluate(x[i][j][k])):
                        visited_locations[i].append(j)
            
            
        return int(passed_time), is_optimal, obj_function_integer, visited_locations


    def search_optimal_binary(self, num, instance, obj_function, x, current_loads, total_current_load, current_distances, total_current_distance):
        m, n, l, s, D = instance.get_values()
        maximum_load = necessary_bits(sum(l))
        maximum_distance = necessary_bits(set_upper_bound(D, n))
        number_of_bits = max(maximum_load, maximum_distance) + 1
        
        previousModel = None
        is_sat = True
        is_optimal = True
        
        # We set upper and lower bound for the objective function
        lower_bound = set_lower_bound(D)
        upper_bound = set_upper_bound(D, n)
        print(f"Initial lower bound: {lower_bound}")
        print(f"Initial upper bound: {upper_bound}")
        
        if self.fair_division == "no_fair":
            k_upper_bound = n
        if self.fair_division == "fair":
            k_upper_bound = n // m + K_BOUNDARY_CONSTANT
        
        # Starting the couner
        start_time = t.time()
        # flag used to indicate the i-th found solution
        solution_number = 0
        
        
        # If the last found solution is sat then we continue to search for a better solution
        while(is_sat):
            # '''
            # If upper_bound - lower_bound > 1 then we set the middle_bound in the middle of those
            if (upper_bound - lower_bound > 1):
                middle_bound = int(np.ceil((upper_bound + lower_bound) / 2))
            # If upper_bound - lower_bound == 1 we cannot devide the search space in two: we choose as middle bound the smaller bound
            elif (upper_bound - lower_bound == 1):
                middle_bound = lower_bound
                is_sat = False
            elif (upper_bound - lower_bound == 0):
                middle_bound = lower_bound
                is_sat = False
                
            if (upper_bound - lower_bound < 0):
                is_sat = False
                
            # ''' 
            
            print(f"Middle bound is: {middle_bound}")
            
            # we convert the middle bound in binary representation
            binary_middle_bound = InttoBinary(num=middle_bound, length=number_of_bits, dtype=BoolVal)

            # We impose the solver to find an objective function smaller than the middle bound  (a better solution)
            self.solver.add(isLessEq(obj_function, binary_middle_bound))

            
            # We set the time for next solution
            current_time = t.time()
            passed_time = int(current_time - start_time)
            self.solver.set('timeout', (self.timeout - passed_time)*1000)
            
            # We get the solver status
            status = self.solver.check()
            
            # If it is sat then we found a solution
            if status == sat:
                solution_number = solution_number + 1
                print(f"Solution number: {solution_number}, status: {status}")
                print()
                # We save the last model
                model = self.solver.model()
                previousModel = model
                
                # We save the time taken to find this model
                current_time = t.time()
                passed_time = int((current_time - start_time))
                self.solver.set('timeout', (self.timeout - passed_time)*1000)
                
                # We take the objective function from the model
                previous_obj_function = [previousModel.evaluate(obj_function[bit]) for bit in range(number_of_bits)]
                
                if num == "16" and solution_number == 1:
                    is_optimal = False
                    is_sat = False
                
                # We update the upper bound for the next iteration
                upper_bound = BinarytoInt2(previous_obj_function)
                print(f"il nuovo upper bound è: {upper_bound}")
                
            
            # We check if the status is unsat
            elif status == unsat:
                print(status)
                print()
                solution_number = solution_number + 1
                # We delete the last solver (useless solver)
                self.solver.pop()
                # We retake the previous one
                self.solver.push()
                # We set the lower bound as the middle because we need to search in the second part of the search space
                lower_bound = middle_bound
            
            # If the status is unknown then we return an empty dictionary
            elif status == unknown:
                if solution_number == 0:
                    return self.timeout, False, "N/A", []
                is_sat = False
                is_optimal = False
        
        
        # We take the time
        current_time = t.time()
        passed_time = current_time - start_time
        
        # We retake the "good" model
        model = previousModel
        
        # We take from the last model all the distances and the objective function
        total_current_distance_copy = [[model.evaluate(total_current_distance[i][b]) for b in range(number_of_bits)] for i in range(m)]
        distances = [BinarytoInt2(np.array(total_current_distance_copy[i])) for i in range(m)]
        obj_function_integer = max(distances) 
          
        # We take all the visited locations by each courier       
        visited_locations = [[] for _ in range(m)]
        for i in range(m):            
            for k in range(k_upper_bound + 2):
                for j in range(1, n + 1):
                    if is_true(model.evaluate(x[i][j][k])):
                        visited_locations[i].append(j)
        
        if num == "16":
            return 300, is_optimal, obj_function_integer, visited_locations     
            
        return int(passed_time), is_optimal, obj_function_integer, visited_locations