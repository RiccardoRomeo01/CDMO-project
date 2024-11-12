from pysmt.shortcuts import Symbol, And, GE, GT, LE, Int, Solver, Equals, Implies, Or, NotEquals, Not, Iff, Plus, Ite, LT, ExactlyOne, ToReal
from pysmt.typing import INT
from pysmt.logics import QF_LIA
from pysmt.exceptions import SolverReturnedUnknownResultError
import time as t
from SMTMOD.SMT.SMT_constants import *
from SMTMOD.SMT.SMT_utils import *
from SMTMOD.SMT.utils import *
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

        # creo il percorso del corriere i-esimo
        # print("la funzione è stata chiamata")
        for i in range(m):
            courier_path = []
            for k in X[i]:
                sol_assignment = model.get_value(k)
                if sol_assignment != Int(n+1):
                    courier_path.append(sol_assignment)
                    
            # print(courier_path)
            shared_visited_locations[i] = courier_path


    def set_constraints_wrapper(self, instance, solver, return_dict):
        X, carried_load, traveled_distance, obj_function = self.set_constraints(instance, solver)
        return_dict['X'] = X
        return_dict['carried_load'] = carried_load
        return_dict['traveled_distance'] = traveled_distance
        return_dict['obj_function'] = obj_function


    def solve_multiprocessing(self, instance):
        start_time = t.time()

        # creo il solver PYSMT
        with Solver(name = self.solver_name, logic = QF_LIA) as solver:

            # Crea un dizionario condiviso per restituire i risultati del setting constraints
            constraints_dict = multiprocessing.Manager().dict()

            # Avvia il processo per set_constraints
            constraint_process = multiprocessing.Process(target = self.set_constraints_wrapper, args=(instance, solver, constraints_dict))
            # faccio partire il processo con l'ottimizzatore
            constraint_process.start()
            current_time = t.time()
            passed_time = int((current_time - start_time))
            process_timeout = self.timeout - passed_time
            constraint_process.join(process_timeout)

            if constraint_process.is_alive():
                print("Timeout! Failed to encode in time")
                constraint_process.terminate()
                constraint_process.join()
            else:
                    X = constraints_dict['X']
                    carried_load = constraints_dict['carried_load']
                    traveled_distance = constraints_dict['traveled_distance']
                    obj_function = constraints_dict['obj_function']

                    # creo i valori condivisi per i multiprocessi
                    s_obj_function = multiprocessing.Value('i', 0)  # 'i' indica un intero, inizialmente è a zero
                    s_is_optimal = multiprocessing.Value('b', False) # 'b' indica che è un booleano, lo inizializzo a False
                    s_visited_locations = multiprocessing.Manager().dict() # uso un dizionario condiviso per i percorsi dei corrieri


                    if self.strategy == "linear":
                        # creo il processo usando come ottimizzatore quello lineare
                        process = multiprocessing.Process(target=self.LO, args=(instance, X, solver, obj_function, s_obj_function, s_is_optimal, s_visited_locations))
                    elif self.strategy == "binary":
                        # creo il processo utilizzando come ottimizzatore quello binario
                        process = multiprocessing.Process(target=self.BO, args=(instance, X, solver, obj_function, s_obj_function, s_is_optimal, s_visited_locations))

                    
                    # faccio partire il processo con l'ottimizzatore
                    process.start()


                    # Aspetta che il processo termini o che scada il timeout, dal timeout devo togliere il tempo impiegato per creare il solver 
                    current_time = t.time()
                    passed_time = int((current_time - start_time))
                    process_timeout = self.timeout - passed_time
                    process.join(process_timeout)

                    # se dopo il tempo di timeout il processo è ancora vivo allora lo killo
                    if process.is_alive():
                        print("Timeout! Killing the optimizer...\n")
                        process.terminate()  # Termina il processo se è ancora attivo
                        process.join()  # Aspetta che il processo termini
                    else:
                        print("Process completed. The optimizer found the best solution!\n")


        # Prendo i valori che mi servono: tempo impiegato dall'ottimizzatore, ultima objective function trovata, ottimalità e le visited_locations
        # visited_locations = get_visited_locations(instance, X, solver)
        current_time = t.time()
        passed_time = current_time - start_time


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
                print_output_SMT(approach, passed_time, optimality, s_obj_function, sol, num, self.output_path + "/SMT/")



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

        
        # se c'è symmetry breaking allora ordino i carichi in ordine decrescente e impongo ai corrieri di portare più peso del successivo corriere
        if self.symmetry_breaking == "sb":
            instance.l.sort(reverse=True)
            for i in range(m-1):
                solver.add_assertion(GT(carried_load[i], carried_load[i+1]))



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


            # prendo lo stato dal solver
            status = solver.check_sat()


            if status is True:
                solution_number = solution_number + 1
                print(f"Solution number: {solution_number}, status: {status}")
                print()


                # salvo questo modello come previousModel
                previousModel = solver.get_model()

                # prendo la objective function dal modello
                previous_obj_function = previousModel.get_value(obj_function)

                # update dell'upper_bound
                upper_bound = previous_obj_function.constant_value()
                print(f"The new upper bound is: {upper_bound}")

                # aggiorno il valore condiviso tra i processi
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
        
        # se sono qui ho avuto il tempo di trovare la soluzione migliore possibile
        shared_is_optimal.value = True
        # come modello riprendo l'ultimo trovato
        model = previousModel
        # aggiorno il valore finale della objective function condivisa tra i processi
        shared_obj_function.value = int(model.get_value(obj_function).serialize())



    def LO(self, instance, X, solver, obj_function, shared_obj_function, shared_is_optimal, shared_visited_locations):

        previousModel = None
        is_sat = True

        # This is a flag used to indicate the i-th found solution
        solution_number = 0

        solver.push()

        while(is_sat):
            # prendo lo stato dal solver
            status = solver.check_sat()

            if status is True:
                # ho trovato una soluzione quindi incremento il counter
                solution_number = solution_number + 1
                # print(solution_number)

                # salvo questo modello come previousModel
                previousModel = solver.get_model()

                # prendo la objective function dal modello
                previous_obj_function = int(solver.get_value(obj_function).serialize())
                print(f"Solution number: {solution_number}, Objective function: {previous_obj_function}")

                # impongo al solver di trovare una soluzione migliore
                solver.add_assertion(LT(obj_function, Int(previous_obj_function)))

                # aggiorno il valore condiviso tra i processi
                shared_obj_function.value = previous_obj_function
                self.set_visited_locations(instance, X, previousModel, shared_visited_locations)


            elif status is False:
                # esco dal ciclo di ricerca delle soluzioni
                is_sat = False

            else:
                # esco dal ciclo di ricerca delle soluzioni
                is_sat = False
                shared_is_optimal.value = False

        # se sono qui ho avuto il tempo di trovare la soluzione migliore possibile
        shared_is_optimal.value = True
        # come modello riprendo l'ultimo trovato
        model = previousModel
        # aggiorno il valore finale della objective function condivisa tra i processi
        shared_obj_function.value = int(model.get_value(obj_function).serialize())