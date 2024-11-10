from pysmt.shortcuts import Symbol, And, GE, LE, Int, Solver, Equals, Implies, Or, NotEquals, Not, Iff, Plus, Ite, LT, ExactlyOne, ToReal
from pysmt.logics import QF_LIA, QF_LRA
from pysmt.typing import INT
from pysmt.exceptions import SolverReturnedUnknownResultError
from pebble import concurrent
from concurrent.futures import TimeoutError, ThreadPoolExecutor, as_completed
from utils import *
from SMT_utils import *
import time as t


LAST_VALUE = None


##### Leggiamo un'istanza ####
instance_num = 4

instance = load_instance(dir="../input", instance_num=instance_num)


exactly_one = ExactlyOne



def set_constraints(instance, solver):
    # prendiamo i dati in ingresso dell'istanza
    m, n, l, s, D = instance.get_values()


    # DECISION VARIABLES

    # X_i_k = j  <->  il corriere i è in posizione j al momento k
    # i = 0,..., m-1 (corrieri)
    # k = 0,..., n+1 (momenti temporali)
    # j = 1,..., n+1 dove n+1 è la base (posizione)
    # X = [[Symbol(f"x_{i}_{k}", INT) for i in range(m)] for k in range(n+2)]
    X = [[Symbol(f"x_{i}_{k}", INT) for k in range(n+2)] for i in range(m)]


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
            [Equals(X[i][k], Int(n+1)) for k in range(1, n+2)]
        )
        solver.add_assertion(back_row_constr)
   
    
    # SE UN CORRIERE È IN BASE AL MOMENTO K ALLORA LO SARÀ ANCHE AL MOMENTO K+1 (esluso il momento 0)
    for i in range(m):
        for k in range(1, n+1):
            solver.add_assertion(
                                Implies(
                                    Equals(X[i][k], Int(n+1)),
                                    Equals(X[i][k+1], Int(n+1))
                                )
            )

    
    # TUTTI I LUOGHI DEVONO ESSERE VISITATI SOLO UNA VOLTA
    for j in range(1, n+1):
        assertions = [Equals(X[i][k], Int(j)) for i in range(m) for k in range(1, n + 1)]
        # solver.add_assertion(exactly_one(assertions, f"one_visit_{j}")) # <------ usa questo per il tuo exactly_one
        solver.add_assertion(exactly_one(assertions)) # <----- usa questo per l'ExactlyOne nativo di pysmt
    

    
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
                                 Int(0)) for k in range(1, n+1)])
            
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
        for k in range(1, n+1):

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



def set_solver(timeout, solver_name):
    # print(timeout)
    if solver_name == 'z3':
        return {'timeout': timeout} 
    elif solver_name == 'cvc5':
        return {'tlimit': str(timeout)}  
    else:
        return {} 
    




def solve_with_pebble(solver_name, timeout):
    # for solver_name in solvers:
        print(f"### SOLVING WITH {solver_name} AS SOLVER ###")
        with Solver(name = solver_name, solver_options = set_solver(timeout, solver_name), logic = QF_LIA) as solver:

            X, carried_load, traveled_distance, obj_function = set_constraints(instance, solver)

            last_value = None
            while(solver.check_sat()):
                try:
                    previous_obj_function = int(solver.get_value(obj_function).serialize())
                    solver.add_assertion(LT(obj_function, Int(previous_obj_function)))

                    found_sol = solver.solve()
                    print(solver.check_sat())
                    # print(f"Quindi, la funzione obiettivo è: {solver.get_value(obj_function)}")
                    if solver.check_sat():
                        last_value = solver.get_value(obj_function)
                        LAST_VALUE = solver.get_value(obj_function)
                    
                except SolverReturnedUnknownResultError as e:
                    print("Non avevo tempo!")
                    break
            
            return last_value




def execute_solver(solver_name, timeout):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(solve_with_pebble, solver_name, timeout)

            try:
                last_value = future.result(timeout=10)  # Attende che la funzione completi e ottiene il risultato
                print(f"The best value is: {LAST_VALUE}")

            except TimeoutError as te:
                print(f"The best value is: {LAST_VALUE}")
                executor.shutdown()



def main():
    timeout = 300 * 1000
    execute_solver('z3', timeout)



if __name__ == '__main__':
    main()

