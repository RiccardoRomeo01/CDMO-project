from pysmt.shortcuts import Symbol, And, GE, GT, LE, Int, Solver, Equals, Implies, Or, NotEquals, Not, Iff, Plus, Ite, LT, ExactlyOne, ToReal
from pysmt.typing import INT
from pysmt.logics import QF_LIA
from pysmt.exceptions import SolverReturnedUnknownResultError
import time as t
import copy
from SMTMOD.SMT.SMT_constants import *
from SMTMOD.SMT.SMT_utils import *
import multiprocessing
import numpy as np



class SMTsolver:
    def __init__(self, input_data, output_path, strategy, timeout=300, symmetry_breaking="False", fair_division="no_fair", solver_name="z3"):
        self.input_data = input_data
        self.timeout = timeout
        self.solver = Solver()
        self.solver_name = solver_name
        self.output_path = output_path
        self.strategy = strategy
        self.symmetry_breaking = symmetry_breaking
        self.fair_division = fair_division
    
        

    def set_visited_locations(self, instance, X, model, shared_visited_locations):
        m, n, l, s, D = instance.get_values()

        # print("la funzione è stata chiamata")
        for i in range(m):
            courier_path = []
            for k in X[i]:
                # sol_assignment = copy.deepcopy(model.get_value(k))
                sol_assignment = int(model.get_value(k).serialize())
                # if sol_assignment != Int(n+1):
                if sol_assignment != n+1:
                    courier_path.append(sol_assignment)
                    
            # print(courier_path)
            shared_visited_locations[i] = copy.deepcopy(courier_path)



    def solve_multiprocessing(self, instance):
        start_time = t.time()

        # we create the PySMT solver
        with Solver(name = self.solver_name, logic = QF_LIA) as solver:

            # I create shared values ​​for multiprocesses
            s_obj_function = multiprocessing.Value('i', 0)  # 'i' indicates an integer, initially it is zero
            s_is_optimal = multiprocessing.Value('b', False) # 'b' indicates that it is a boolean, I initialize it to False
            s_visited_locations = multiprocessing.Manager().dict() # I use a shared dictionary for courier routes


            # I set the solver contracts
            X, carried_load, traveled_distance, obj_function = self.set_constraints(instance, solver)


            if self.strategy == "linear":
                # I create the process using the linear one as an optimizer
                process = multiprocessing.Process(target=self.LO, args=(instance, X, solver, obj_function, traveled_distance, s_obj_function, s_is_optimal, s_visited_locations))
            elif self.strategy == "binary":
                # I create the process using the binary one as the optimizer
                process = multiprocessing.Process(target=self.BO, args=(instance, X, solver, obj_function, s_obj_function, s_is_optimal, s_visited_locations))

            
            # I start the process with the optimizer
            process.start()


            # Wait for the process to finish or for the timeout to expire, from the timeout I have to subtract the time taken to create the solver 
            current_time = t.time()
            passed_time = int((current_time - start_time))
            process_timeout = self.timeout - passed_time
            process.join(process_timeout)

            # if after the timeout the process is still alive then I kill it
            if process.is_alive():
                print("Timeout! Killing the optimizer...\n")
                process.terminate()  # Kill the process if it is still active
                process.join()  # Wait for the process to finish
            else:
                print("Process completed. The optimizer found the best solution!\n")


        # I take the values ​​I need: time taken by the optimizer, last objective function found, optimality and the visited_locations
        # visited_locations = get_visited_locations(instance, X, solver)
        current_time = t.time()
        passed_time = current_time - start_time

        # I check the returned values
        if int(passed_time) >= 300 and s_is_optimal.value == False and s_obj_function.value == 0 and not s_visited_locations:
            return int(passed_time), s_is_optimal.value, "N/A failed to encode", s_visited_locations
    

        return int(passed_time), s_is_optimal.value, s_obj_function.value, s_visited_locations



    def solve(self):

        if self.solver_name == "all" and self.strategy == "all" and self.fair_division == "all" and self.symmetry_breaking == "all":

            for solver_name in SMT_SOLVERS:
                self.solver_name = solver_name
                print(f"\n\n \t\t##### SOLVING USING {self.solver_name} AS SOLVER #####")

                for num, instance in self.input_data.items():

                    for strategy in STRATEGIES:
                        self.strategy = strategy
                        print(f"\nWe are using {self.strategy} optimization")

                        for f in LOAD_DIVISION:

                            self.fair_division = f
                            for s in SYMMETRY_BREAKING:

                                self.symmetry_breaking = s
                                print(f"\n\t## Solution for instance {num} ##")

                                passed_time, s_is_optimal, s_obj_function, s_visited_locations = self.solve_multiprocessing(instance)
                                sol = from_dict_to_list(s_visited_locations)

                                if s_is_optimal == 1:
                                    optimality = True
                                else:
                                    optimality = False


                                print(f"The solver took {passed_time} seconds to solve the instance")
                                print(f"The optimal flag is: {optimality}")
                                print(f"The objective function is: {s_obj_function}")
                                print(f"The solution is: {sol}")
                                
                                print("\n")
                                approach = solver_name + " " + self.strategy + " " + self.fair_division + " " + self.symmetry_breaking
                                if s_obj_function != "N/A failed to encode" and s_obj_function != 0:
                                    print_output_SMT(approach, passed_time, optimality, s_obj_function, sol, num, self.output_path + "/SMT/")


        elif self.solver_name != "all" and self.strategy != "all" and self.fair_division != "all" and self.symmetry_breaking != "all":

            print(f"\n\n \t\t##### SOLVING USING {self.solver_name} AS SOLVER #####")
            print(f"\nWe are using {self.strategy} optimization")
            for num, instance in self.input_data.items():
                print(f"\n\t## Solution for instance {num} ##")
                passed_time, s_is_optimal, s_obj_function, s_visited_locations = self.solve_multiprocessing(instance)
                sol = from_dict_to_list(s_visited_locations)

                if s_is_optimal == 1:
                    optimality = True
                else:
                    optimality = False

                print(f"The solver took {passed_time} seconds to solve the instance")
                print(f"The optimal flag is: {optimality}")
                print(f"The objective function is: {s_obj_function}")
                print(f"The solution is: {sol}")
                                
                print("\n")
                approach = self.solver_name + " " + self.strategy + " " + self.fair_division + " " + self.symmetry_breaking
                if s_obj_function != "N/A failed to encode" and s_obj_function != 0:
                    print_output_SMT(approach, passed_time, optimality, s_obj_function, sol, num, self.output_path + "/SMT/")
        
        elif self.solver_name != "all" and self.strategy == "all" and self.fair_division == "all" and self.symmetry_breaking == "all":
            print(f"\n\n \t\t##### SOLVING USING {self.solver_name} AS SOLVER #####")
            for num, instance in self.input_data.items():

                for strategy in STRATEGIES:
                    self.strategy = strategy
                    print(f"\nWe are using {self.strategy} optimization")

                    for f in LOAD_DIVISION:

                        self.fair_division = f
                        for s in SYMMETRY_BREAKING:

                            self.symmetry_breaking = s
                            print(f"\n\t## Solution for instance {num} ##")

                            passed_time, s_is_optimal, s_obj_function, s_visited_locations = self.solve_multiprocessing(instance)
                            sol = from_dict_to_list(s_visited_locations)

                            if s_is_optimal == 1:
                                optimality = True
                            else:
                                optimality = False


                            print(f"The solver took {passed_time} seconds to solve the instance")
                            print(f"The optimal flag is: {optimality}")
                            print(f"The objective function is: {s_obj_function}")
                            print(f"The solution is: {sol}")
                                
                            print("\n")
                            approach = self.solver_name + " " + self.strategy + " " + self.fair_division + " " + self.symmetry_breaking
                            if s_obj_function != "N/A failed to encode" and s_obj_function != 0:
                                print_output_SMT(approach, passed_time, optimality, s_obj_function, sol, num, self.output_path + "/SMT/")



    def set_constraints(self, instance, solver):

        # I set the implementation of exactly_one
        exactly_one = ExactlyOne
        at_least_k = at_least_k_np
        # we take the input data of the instance
        m, n, l, s, D = instance.get_values()

        if self.fair_division == "no_fair":
            k_upper_bound = n
        
        if self.fair_division == "fair":
            fair_division_coefficient = n // m
            k_upper_bound = fair_division_coefficient + 1
            print(f"Each courier has to bring at least {fair_division_coefficient} items")


        # DECISION VARIABLES

        # X_i_k = j  <->  courier i is in position j at time k
        # i = 0,..., m-1 (couriers)
        # k = 0,..., n+1 (temporal moments)
        # j = 1,..., n+1 where n+1 is the base (position)
        # X = [[Symbol(f"x_{i}_{k}", INT) for i in range(m)] for k in range(n+2)]
        X = [[Symbol(f"x_{i}_{k}", INT) for k in range(k_upper_bound+2)] for i in range(m)]


        # carried_load[i] will hold the total weight carried by the i-th courier
        carried_load = [Symbol(f"carried_load_{i}", INT) for i in range(m)]

        # traveled_distance[i] will hold the total distance traveled by the i-th courier
        traveled_distance = [Symbol(f"traveled_distance_{i}", INT) for i in range(m)]

        # obj_function it will be the maximum value among all the distances travelled
        obj_function = Symbol(f"obj_function", INT)


        # we define the domain of X, j = 1,..., n+1 where n+1 is the base (position)
        domain_X = []
        for row in X:
            row_domain = And([And(GE(x, Int(1)),
                                    LE(x, Int(n+1))) for x in row])
            domain_X.append(row_domain)

        # we impose the domain of X on the solver
        solver.add_assertion(And(domain_X))



        # ALL COURIERS MUST START IN BASE (currently k=0 the courier is in j=n+1)
        for i in range(m):
            solver.add_assertion(Equals(X[i][0], Int(n+1)))


        # ALL COURIERS SOONER OR LATER MUST RETURN TO BASE (at a time k>=1 the courier must be at j=n+1 at least once)
        for i in range(m):
            back_row_constr = Or(
                [Equals(X[i][k], Int(n+1)) for k in range(1, k_upper_bound+2)]
            )
            solver.add_assertion(back_row_constr)
    
        
        # IF A COURIER IS BASED ON MOMENT K THEN IT WILL ALSO BE BASED ON MOMENT K+1 (excluding moment 0)
        for i in range(m):
            for k in range(1, k_upper_bound+1):
                solver.add_assertion(
                                    Implies(
                                        Equals(X[i][k], Int(n+1)),
                                        Equals(X[i][k+1], Int(n+1))
                                    )
                )

        
        # ALL PLACES SHOULD ONLY BE VISITED ONCE
        for j in range(1, n+1):
            assertions = [Equals(X[i][k], Int(j)) for i in range(m) for k in range(1, k_upper_bound + 1)]
            # solver.add_assertion(exactly_one(assertions, f"one_visit_{j}")) # <------ usa questo per il tuo exactly_one
            solver.add_assertion(exactly_one(assertions)) # <----- usa questo per l'ExactlyOne nativo di pysmt
        

        ### FAIR LOAD DIVISION CONSTRAINT ###
        if self.fair_division == "fair":
            # if couriers must carry at least a certain number of parcels then in X[i] at least a certain number of elements must be different from 7
            for i in range(m):
                load_division_assertions = [NotEquals(X[i][k], Int(n+1)) for k in range(1, k_upper_bound + 1)]
                solver.add_assertion(at_least_k(load_division_assertions, fair_division_coefficient, f"fair_load_{i}"))

        
        #### SYMMETRY BREAKING CONSTRAINT ####
        if self.symmetry_breaking == "sb":
            # If the carriable load of two couriers is the same then we impose one of them to carry more load respect to the other
            for i1 in range(m):
                for i2 in range(i1 + 1, m):
                    # the constraint must be applied to two different couriers
                    if i1 != i2:
                        solver.add_assertion(Implies(Equals(Int(l[i1]), Int(l[i2])),
                                                    GT(carried_load[i1], carried_load[i2])))



        # carried_load[i] will have the sum of all the weights transported by the couriers
        for i in range(m):
            # In implications I put the implications that I use to calculate the sums of the weights
            implications = []
            for j in range(1, n+1):
                # I put the sum here for each location visited
                # If X[i][k] is equal to j then in Plus I put s[j-1], otherwise I put 0
                # In sum_expr I put the sum of all the weights transported
                sum_expr = Plus([Ite(Equals(X[i][k], Int(j)),
                                    Int(s[j - 1]), 
                                    Int(0)) for k in range(1, k_upper_bound+1)])
                
                implications.append(sum_expr)

            # Add the assertion to the solver: carried_load[i] = sum of carried weights
            solver.add_assertion(Equals(carried_load[i], Plus(implications)))



        # EACH COURIER CANNOT CARRY MORE THAN A CERTAIN WEIGHT
        for i in range(m):
            solver.add_assertion(LE(carried_load[i], Int(l[i])))


        
        # traveled_distance[i] will have the sum of the distances traveled by courier i
        for i in range(m):
            distances = []

            # I take the distance from the initial position
            for j in range(1, n+2):
                first_distance = Plus([Ite(Equals(X[i][1], Int(j)),
                                            Int(int(D[n][j-1])),
                                            Int(0))])
                distances.append(first_distance)
                
            # I distance myself between two consecutively visited locations
            for k in range(1, k_upper_bound+1):

                for j1 in range(1, n + 2):
                    for j2 in range(1, n + 2):
                        distances.append(Plus([Ite(And(Equals(X[i][k], Int(j1)),
                                                    Equals(X[i][k+1], Int(j2))),
                                                    Int(int(D[j1-1][j2-1])),
                                                    Int(0)
                                                )]))

            solver.add_assertion(Equals(traveled_distance[i], Plus(distances)))


        #### Here we find the maximum distance among all couriers ####
        # Auxiliary variable to find the maximum
        max_val = Symbol("max_val", INT)

        # max_val must be greater than each distance d among couriers
        for d in traveled_distance:
            solver.add_assertion(GE(max_val, d))

        # We impose to max_val to be equal to one of the traveled distances
        solver.add_assertion(Or([Equals(max_val, d) for d in traveled_distance]))

        # we impose obj function equal to max_val
        solver.add_assertion(Equals(obj_function, max_val))


        # return variables
        return X, carried_load, traveled_distance, obj_function



    def BO(self, instance, X, solver, obj_function, shared_obj_function, shared_is_optimal, shared_visited_locations):

        m, n, l, s, D = instance.get_values()

        # We set upper and lower bound for the objective function
        lower_bound = set_lower_bound(D)
        upper_bound = set_upper_bound(D, n)

        # This is a flag used to indicate the i-th found solution
        solution_number = 0

        previousModel = None
        is_sat = True

        solver.push()


        while(is_sat):

            # If upper_bound - lower_bound > 1 then we set the middle_bound in the middle of those
            if (upper_bound - lower_bound > 1):
                middle_bound = int(np.ceil((upper_bound + lower_bound) / 2))
            # If upper_bound - lower_bound == 1 we cannot devide the search space in two: we choose as middle bound the smaller bound
            elif (upper_bound - lower_bound == 1):
                middle_bound = int(lower_bound)
                is_sat = False
            elif (upper_bound - lower_bound == 0):
                middle_bound = int(lower_bound)
                is_sat = False
                    
            if (upper_bound - lower_bound < 0):
                is_sat = False

            print(f"Middle bound is: {middle_bound}")


            # We impose the solver to find an objective function smaller than the middle bound  (a better solution)
            solver.add_assertion(LE(obj_function, Int(middle_bound)))


            # I get the state from the solver
            status = solver.check_sat()


            if status is True:
                solution_number = solution_number + 1
                print(f"Solution number: {solution_number}, status: {status}")
                print()


                # I save this model as previousModel
                previousModel = solver.get_model()

                # I take the objective function from the model
                previous_obj_function = previousModel.get_value(obj_function)

                # update upper_bound update
                upper_bound = previous_obj_function.constant_value()
                print(f"The new upper bound is: {upper_bound}")

                # I update the shared value between processes
                shared_obj_function.value = int(solver.get_value(obj_function).serialize())
                self.set_visited_locations(instance, X, previousModel, shared_visited_locations)
            
            elif status is False:
                print(status)
                print()

                # We delete the last solver (useless solver)
                solver.pop()
                # We retake the previous one
                solver.push()
                # We set the lower bound as the middle because we need to search in the second part of the search space
                lower_bound = int(middle_bound)
            
            else:
                is_sat = False
                shared_is_optimal.value = False
        
        # if I'm here I've had time to find the best possible solution
        shared_is_optimal.value = True
        # I use the latest finding as a model
        model = previousModel
        # I update the final value of the objective function shared between processes
        shared_obj_function.value = int(model.get_value(obj_function).serialize())



    def LO(self, instance, X, solver, obj_function, traveled_distance, shared_obj_function, shared_is_optimal, shared_visited_locations):

        previousModel = None
        is_sat = True

        # This is a flag used to indicate the i-th found solution
        solution_number = 0

        solver.push()

        while(is_sat):
            # I get the state from the solver
            status = solver.check_sat()

            if status is True:
                # I found a solution so I increase the counter
                solution_number = solution_number + 1
                # print(solution_number)

                # I save this model as previousModel
                previousModel = solver.get_model()

                # I take the objective function from the model
                
                previous_obj_function = int(solver.get_value(obj_function).serialize())
                
                # I update the shared value between processes
                shared_obj_function.value = previous_obj_function
                self.set_visited_locations(instance, X, previousModel, shared_visited_locations)
                print(f"Solution number: {solution_number}, Objective function: {previous_obj_function}, {from_dict_to_list(shared_visited_locations)}")
                # print(f"Solution number: {solution_number}, Objective function: {previous_obj_function}")

                '''
                for distance in traveled_distance:
                    print(int(solver.get_value(distance).serialize()))
                '''

                # I force the solver to find a better solution
                solver.add_assertion(LT(obj_function, Int(previous_obj_function)))


            elif status is False:
                # I get out of the cycle of finding solutions
                is_sat = False

            else:
                # I get out of the cycle of finding solutions
                is_sat = False
                shared_is_optimal.value = False

        # if I'm here I've had time to find the best possible solution
        shared_is_optimal.value = True
        # I use the latest finding as a model
        model = previousModel
        # I update the final value of the objective function shared between processes
        shared_obj_function.value = int(model.get_value(obj_function).serialize())