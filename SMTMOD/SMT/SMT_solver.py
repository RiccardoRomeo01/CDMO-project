from pysmt.shortcuts import Symbol, And, GE, LE, Int, Solver
from pysmt.typing import INT
from SMT.utils import *
import time as t



class SMTsolver:
    def __init__(self, input_data, output_path, strategy, timeout=300, symmetry_breaking="False", fair_division="no_fair", model="z3"):
        self.input_data = input_data
        self.timeout = timeout
        self.solver = Solver()
        self.model = model
        self.output_path = output_path
        self.strategy = strategy
        self.symmetry_breaking = symmetry_breaking
        self.fair_division = fair_division

    def set_solver(self):
        self.solver = Solver(name=self.model)
