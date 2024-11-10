from pysmt.shortcuts import Symbol, And, GE, LE, Int, Solver, Equals, Implies, Or, NotEquals, Not, Iff, Plus, Ite, LT, ExactlyOne, ToReal
from pysmt.typing import INT
from pysmt.logics import QF_LIA
from pysmt.exceptions import SolverReturnedUnknownResultError
import time as t
from SMTMOD.SMT.SMT_constants import *
from SMTMOD.SMT.SMT_utils import *
from SMTMOD.SMT.utils import *
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



    def set_solver(self, timeout, solver_name):
        self.solver_name = solver_name
        self.timeout = timeout

        # print(self.timeout)
        if self.solver_name == 'z3':
            return {'timeout': self.timeout} 
        elif self.solver_name == 'cvc5':
            return {'tlimit': str(self.timeout)}  
        else:
            return {} 
    


    def solve(self):

        if self.solver_name == "all" and self.strategy == "all" and self.fair_division == "all":
            # per ogni solver passato
            for solver_name in SMT_SOLVERS:
                # print(self.timeout)
                print(f"\n\n \t\t##### SOLVING USING {solver_name} AS SOLVER #####")
                # per ogni istanza passata in ingresso creiamo un solver e risolviamo il problema
                for num, instance in self.input_data.items():

                    # per ogni strategia di ottimizzazione
                    for strategy in STRATEGIES:

                        # setto la strategia da usare
                        self.strategy = strategy
                        print(f"\nWe are using {self.strategy} optimization")

                        for f in LOAD_DIVISION:

                            self.fair_division = f

                            print(f"\n\t## Solution for instance {num} ##")
                            # devo risettare il timeout qui
                            self.timeout = 300
                            with Solver(name = solver_name, solver_options = self.set_solver(self.timeout*1000, solver_name), logic = QF_LIA) as solver:
                                # print(self.timeout)
                                # settiamo i constraints per questa istanza
                                X, carried_load, traveled_distance, obj_function = self.set_constraints(instance, solver)

                                # settiamo il metodo di ottimizzazione in base a quello passato
                                if self.strategy == "linear":
                                    time, optimal, obj, sol = self.linear_optimization(instance, solver, self.timeout, X, carried_load, traveled_distance, obj_function)
                                elif self.strategy == "binary":
                                    time, optimal, obj, sol = self.binary_optimization(instance, solver, self.timeout, X, carried_load, traveled_distance, obj_function)
                            


                            print(f"The solver took {time} seconds to solve the instance")
                            print(f"The optimal flag is: {optimal}")
                            print(f"The objective function is: {obj}")
                            print(f"The solution is: {sol}")

                            approach = solver_name + " " + self.strategy + " " + self.fair_division

                            print_output_SMT(approach, time, optimal, obj, sol, num, self.output_path + "/SMT/")





    def set_constraints(self, instance, solver):

        # setto l'implementaione di exactly_one
        exactly_one = ExactlyOne
        at_least_k = at_least_k_np
        # prendiamo i dati in ingresso dell'istanza
        m, n, l, s, D = instance.get_values()

        if self.fair_division == "no_fair":
            k_upper_bound = n
        
        if self.fair_division == "fair":
            fair_division_coefficient = n // m
            k_upper_bound = fair_division_coefficient + 1
            print(f"Each courier has to bring at least {fair_division_coefficient} items")

        # DECISION VARIABLES

        # X_i_k = j  <->  il corriere i è in posizione j al momento k
        # i = 0,..., m-1 (corrieri)
        # k = 0,..., n+1 (momenti temporali)
        # j = 1,..., n+1 dove n+1 è la base (posizione)
        # X = [[Symbol(f"x_{i}_{k}", INT) for i in range(m)] for k in range(n+2)]
        X = [[Symbol(f"x_{i}_{k}", INT) for k in range(k_upper_bound+2)] for i in range(m)]


        # carried_load[i] terrà il peso totale portato dal corriere i-esimo
        carried_load = [Symbol(f"carried_load_{i}", INT) for i in range(m)]

        # traveled_distance[i] terrà la distanza totale percorsa dal corriere i-esimo
        traveled_distance = [Symbol(f"traveled_distance_{i}", INT) for i in range(m)]

        # obj_function sarà il valore massimo tra tutte le distanze percorse
        obj_function = Symbol(f"obj_function", INT)


        # definiamo il dominio di X, j = 1,..., n+1 dove n+1 è la base (posizione)
        domain_X = []
        for row in X:
            row_domain = And([And(GE(x, Int(1)),
                                    LE(x, Int(n+1))) for x in row])
            domain_X.append(row_domain)

        # imponiamo il dominio di X al solver
        solver.add_assertion(And(domain_X))



        # TUTTI I CORRIERI DEVONO INIZIARE IN BASE (al momento k=0 il corriere è in j=n+1)
        for i in range(m):
            solver.add_assertion(Equals(X[i][0], Int(n+1)))


        # TUTTI I CORRIERI PRIMA O POI DEVONO TORNARE IN BASE (in un momento k>=1 il corriere dev'essere almeno una volta in j=n+1)
        for i in range(m):
            back_row_constr = Or(
                [Equals(X[i][k], Int(n+1)) for k in range(1, k_upper_bound+2)]
            )
            solver.add_assertion(back_row_constr)
    
        
        # SE UN CORRIERE È IN BASE AL MOMENTO K ALLORA LO SARÀ ANCHE AL MOMENTO K+1 (esluso il momento 0)
        for i in range(m):
            for k in range(1, k_upper_bound+1):
                solver.add_assertion(
                                    Implies(
                                        Equals(X[i][k], Int(n+1)),
                                        Equals(X[i][k+1], Int(n+1))
                                    )
                )

        
        # TUTTI I LUOGHI DEVONO ESSERE VISITATI SOLO UNA VOLTA
        for j in range(1, n+1):
            assertions = [Equals(X[i][k], Int(j)) for i in range(m) for k in range(1, k_upper_bound + 1)]
            # solver.add_assertion(exactly_one(assertions, f"one_visit_{j}")) # <------ usa questo per il tuo exactly_one
            solver.add_assertion(exactly_one(assertions)) # <----- usa questo per l'ExactlyOne nativo di pysmt
        

        ### FAIR LOAD DIVISION CONSTRAINT ###
        if self.fair_division == "fair":
            # se i corrieri devono portare almeno un certo numero di pacchi allora in X[i] almeno un certo numero di elementi dev'essere diverso da 7
            for i in range(m):
                load_division_assertions = [NotEquals(X[i][k], Int(n+1)) for k in range(1, k_upper_bound + 1)]
                solver.add_assertion(at_least_k(load_division_assertions, fair_division_coefficient, f"fair_load_{i}"))



        # carried_load[i] avrà la somma di tutti i pesi trasportati dal corrieri i
        for i in range(m):
            # In implications metto le implicazioni che uso per calcolare le somme dei pesi
            implications = []
            for j in range(1, n+1):
                # Metto qui la somma per ogni posizione visitata
                # Se X[i][k] è uguale a j allora in Plus metto s[j-1], altrimenti metto 0
                # In sum_expr metto la somma di tutti i pesi trasportati
                sum_expr = Plus([Ite(Equals(X[i][k], Int(j)),
                                    Int(s[j - 1]), 
                                    Int(0)) for k in range(1, k_upper_bound+1)])
                
                implications.append(sum_expr)

            # Aggiungi l'assertion al solver: carried_load[i] = somma dei pesi trasportati
            solver.add_assertion(Equals(carried_load[i], Plus(implications)))



        # OGNI CORRIERE NON PUÒ TRASPORTARE PIÙ DI UN CERTO PESO
        for i in range(m):
            solver.add_assertion(LE(carried_load[i], Int(l[i])))


        
        # traveled_distances[i] avrà la somma delle distanza percorse dal corriere i
        for i in range(m):
            distances = []

            # prendo la distanza dalla posizione iniziale
            for j in range(1, n+2):
                first_distance = Plus([Ite(Equals(X[i][1], Int(j)),
                                            Int(int(D[n][j-1])),
                                            Int(0))])
                distances.append(first_distance)
                
            # prendo le distanze tra due posizioni visitate consecutivamente
            for k in range(1, k_upper_bound+1):

                for j1 in range(1, n + 2):
                    for j2 in range(1, n + 2):
                        distances.append(Plus([Ite(And(Equals(X[i][k], Int(j1)),
                                                    Equals(X[i][k+1], Int(j2))),
                                                    Int(int(D[j1-1][j2-1])),
                                                    Int(0)
                                                )]))

            solver.add_assertion(Equals(traveled_distance[i], Plus(distances)))


        # impongo che la obj_function sia il valore maggiore tra le distanze percorse dai corrieri
        for i in range(m):
            solver.add_assertion(GE(obj_function, traveled_distance[i]))


        # return variables
        return X, carried_load, traveled_distance, obj_function




    def linear_optimization(self, instance, solver, timeout, X, carried_load, traveled_distance, obj_function):

        m, n, l, s, D = instance.get_values()

        previousModel = None
        is_sat = True
        is_optimal = True

        # Start of the counter
        start_time = t.time()
        # This is a flag used to indicate the i-th found solution
        solution_number = 0
        
        # salvo lo stato del solver prima della ricerca
        solver.push()

        while(is_sat):

            try: 
                # prendo lo stato dal solver
                status = solver.check_sat()

                if status is True:
                    # ho trovato una soluzione quindi incremento il counter
                    solution_number = solution_number + 1
                    # print(solution_number)

                    # salvo questo modello come previousModel
                    previousModel = solver.get_model()

                    # calcolo quanto tempo è passato
                    current_time = t.time()
                    passed_time = int((current_time - start_time))

                    # setto il timeout per il solver
                    # self.set_solver((timeout - passed_time)*1000, solver)
                    self.set_solver((timeout - passed_time), solver)

                    # prendo la objective function dal modello
                    previous_obj_function = previousModel.get_value(obj_function)
                    # print(previous_obj_function)
                    # print(type(previous_obj_function))

                    # impongo al solver di trovare una soluzione migliore
                    solver.add_assertion(LT(obj_function, previous_obj_function))

                elif status is False:
                    # se il counter di soluzioni è a zero vuol dire che non ho mai trovato almeno una soluzione
                    if solution_number == 0:
                        print(status)
                        current_time = t.time()
                        passed_time = int((current_time - start_time))
                        return passed_time, False, "N/A unsat", []
                    # esco dal ciclo di ricerca delle soluzioni
                    is_sat = False

                else:
                    # se il counter di soluzioni è a zero vuol dire che non ha avuto il tempo di trovarla
                    if solution_number == 0:
                        print("TIME EXCEEDED")
                        return timeout, False, "N/A unknown", []
                    
                    # esco dal ciclo di ricerca delle soluzioni
                    is_sat = False
                    is_optimal = False

            except SolverReturnedUnknownResultError:
                print("Solver encountered an unknown result error. Using the last known solution.")
                is_optimal = False
                break

        current_time = t.time()
        passed_time = current_time - start_time

        # come modello riprendo l'ultimo trovato
        model = previousModel if previousModel is not None else None
        

        if model is not None:
            visited_locations = [[] for _ in range(m)]
            for i in range(m):
                for k in X[i]:
                    sol_assignment = model.get_value(k)
                    if sol_assignment != Int(n+1):
                        visited_locations[i].append(sol_assignment)
            
            return int(passed_time), is_optimal, model.get_value(obj_function), visited_locations
        else:
            return int(passed_time), False, "N/A no_solution", []



    def binary_optimization(self, instance, solver, timeout, X, carried_load, traveled_distance, obj_function):

        m, n, l, s, D = instance.get_values()
        
        previousModel = None
        is_sat = True
        is_optimal = True

        # We set upper and lower bound for the objective function
        lower_bound = set_lower_bound(D)
        upper_bound = set_upper_bound(D, n)

        # Start of the counter
        start_time = t.time()
        # This is a flag used to indicate the i-th found solution
        solution_number = 0

        # salvo lo stato del solver prima della ricerca
        solver.push()
        
        while(is_sat):

            try: 
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

                # print(f"Middle bound is: {middle_bound}")


                # We impose the solver to find an objective function smaller than the middle bound  (a better solution)
                solver.add_assertion(LE(obj_function, Int(middle_bound)))

                # We set the time for next solution
                current_time = t.time()
                passed_time = int(current_time - start_time)
                # self.set_solver((timeout - passed_time)*1000, solver)
                self.set_solver((timeout - passed_time), solver)

                
                # prendo lo stato dal solver
                status = solver.check_sat()


                if status is True:
                    solution_number = solution_number + 1
                    # print(f"Solution number: {solution_number}, status: {status}")
                    # print()


                    # salvo questo modello come previousModel
                    previousModel = solver.get_model()

                    # We set the time for next solution
                    current_time = t.time()
                    passed_time = int(current_time - start_time)
                    # self.set_solver((timeout - passed_time)*1000, solver)
                    self.set_solver((timeout - passed_time), solver)

                    # prendo la objective function dal modello
                    previous_obj_function = previousModel.get_value(obj_function)

                    # update dell'upper_bound
                    upper_bound = previous_obj_function.constant_value()
                    # print(f"il nuovo upper bound è: {upper_bound}")
                    
                elif status is False:
                    # print(status)
                    # print()
                    solution_number = solution_number + 1


                    # We delete the last solver (useless solver)
                    solver.pop()
                    # We retake the previous one
                    solver.push()
                    # We set the lower bound as the middle because we need to search in the second part of the search space
                    lower_bound = int(middle_bound)

                else:
                    if solution_number == 0:
                        return timeout, False, "N/A", []
                    
                    is_sat = False
                    is_optimal = False
            except SolverReturnedUnknownResultError:
                print("Solver encountered an unknown result error. Using the last known solution.")
                is_optimal = False
                break  

        current_time = t.time()
        passed_time = current_time - start_time

        # come modello riprendo l'ultimo trovato
        model = previousModel if previousModel is not None else None
        
        if model is not None:
            visited_locations = [[] for _ in range(m)]
            for i in range(m):
                for k in X[i]:
                    sol_assignment = model.get_value(k)
                    if sol_assignment != Int(n+1):
                        visited_locations[i].append(sol_assignment)
            
            return int(passed_time), is_optimal, model.get_value(obj_function), visited_locations
        else:
            return int(passed_time), False, "N/A no_solution", []