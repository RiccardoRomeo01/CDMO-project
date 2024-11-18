import argparse
from utils import *


from CPMOD.cp.solver import CPsolver
from MIPMOD.MIP_CLASS import MIPSolver
from SATMOD.SAT.SAT_solver import SATsolver

from SMTMOD.SMT.SMT_solver import SMTsolver


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--approach", help="Select a modelling approach between cp sat, smt and mip",
                        default="cp", type=str)

    parser.add_argument("-m", "--model", help="Select a model for the solver choosen, look for additional information in the cp folder ",
                        default=1, type=int)
    parser.add_argument("-sv", "--solver", help="Select a solver for the mip model",default="all", type=str)

    parser.add_argument("-n", "--num_instance",
                        help="Select the instance that you want to solve, default = 0 solve all",
                        default=1, type=int)

    parser.add_argument("-i", "--input_dir",
                        help="Directory where the instance txt files can be found",
                        default="./input", type=str)

    parser.add_argument("-o", "--output_dir",
                        help="Directory where the output will be saved", default="./res")

    parser.add_argument("-t", "--timeout", help="Timeout in seconds", default=300, type=int)

    parser.add_argument("-s", "--strategy", help="Search strategy", default="all", type= str)

    parser.add_argument("-b", "--symmetry_breaking", help="Symmetry breaking flag", default="sb", type=str)

    parser.add_argument("-e", "--encoding", help="Encoding to use", default="all", type= str)

    parser.add_argument("-f", "--fair_division", help="Impose or not a fair load division between the couriers", default="all", type= str)

    args = parser.parse_args()
    print(args)
    
    # dowloading the instances data from the directory
    print("We load the instances.")
    if args.approach == "cp":
        input_data = load_data_cp(args.input_dir, args.num_instance)
    elif args.approach == "mip" or args.approach == "sat" or args.approach == "smt":
        input_data = load_data_sat_mip(args.input_dir, args.num_instance)
    print("Loaded!")


    if args.approach == "smt":
        solver = SMTsolver(
            input_data = input_data,
            timeout = int(args.timeout),
            output_path = args.output_dir,
            solver_name=args.solver,
            strategy = args.strategy,
            symmetry_breaking = args.symmetry_breaking,
            fair_division = args.fair_division
        )
    elif args.approach == "cp":
        solver = CPsolver(
            data=input_data, 
            output_dir=args.output_dir, 
            timeout=int(args.timeout), 
            model=args.model
        ) 
    elif args.approach == "sat":
        solver = SATsolver(
            input_data = input_data,
            timeout = int(args.timeout),
            encoding = args.encoding,
            output_path = args.output_dir,
            strategy= args.strategy,
            symmetry_breaking = args.symmetry_breaking,
            fair_division = args.fair_division
        ) 
    elif args.approach == "mip":
        solver = MIPSolver(
            instance_number=args.num_instance,
            data=input_data, 
            output_dir=args.output_dir, 
            timeout=int(args.timeout), 
            model=args.solver,
            symmetry_breaking = args.symmetry_breaking
        )
    elif args.approach == 'all':
        solver = CPsolver(
            data=load_data_cp(args.input_dir, args.num_instance), 
            output_dir=args.output_dir, 
            timeout=int(args.timeout), 
            model=args.model
        ) 

        print("Solving with CP ...")
        solver.solve()
        

        solver = SMTsolver(
            input_data = load_data_sat_mip(args.input_dir, args.num_instance),
            timeout = int(args.timeout),
            output_path = args.output_dir,
            solver_name= "all",
            strategy = "all",
            symmetry_breaking = "all",
            fair_division = "all"
        )

        print("Solving with SMT ...")
        solver.solve()

        solver = SATsolver(
            input_data = load_data_sat_mip(args.input_dir, args.num_instance),
            timeout = int(args.timeout),
            encoding = "all",
            output_path = args.output_dir,
            strategy= "all",
            symmetry_breaking = "all",
            fair_division = "all"
        ) 

        print("Solving with SAT ...")
        solver.solve()

        solver = MIPSolver(
            instance_number=0,
            data=load_data_sat_mip(args.input_dir, args.num_instance), 
            output_dir=args.output_dir, 
            timeout=int(args.timeout), 
            model="all",
            symmetry_breaking = "all"
        )

        print("Solving with MIP ...")
        solver.solve()
    else:
        raise argparse.ArgumentError(None, "Please select a solver between cp, sat, smt or mip")
    
        # Error printing
    if args.approach == "sat":
        if args.num_instance < 0 or args.num_instance > 21: 
            raise argparse.ArgumentError(None, "The number of instance must be an integer in the range [0, 21]")
        if args.timeout <= 0:
            raise TimeoutError("Timeout in seconds must be a positive integer")
        if args.encoding != "np" and args.encoding != "seq" and args.encoding != "bw" and args.encoding != "he" and args.encoding != "pb" and args.encoding != "all":
            raise argparse.ArgumentError(None, "The encoding argument must be: np, seq, bw, he, pb or all")
        if args.strategy != "linear" and args.strategy != "binary" and args.strategy != "all":
            raise argparse.ArgumentError(None, "The strategy argument must be: linear, binary or all")
        if args.symmetry_breaking != "sb" and args.symmetry_breaking != "no_sb" and args.symmetry_breaking != "all":
            raise argparse.ArgumentError(None, "The symmetry_breaking argument must be: sb, no_sb or all")
        if args.fair_division != "fair" and args.fair_division != "no_fair" and args.fair_division != "all":
            raise argparse.ArgumentError(None, "The fair_division argument must be: fair, no_fair or all")

    if args.approach == "mip":
        if args.num_instance < 0 or args.num_instance > 21: 
            raise argparse.ArgumentError(None, "The number of instance must be an integer in the range [0, 21]")
        if args.timeout <= 0:
            raise TimeoutError("Timeout in seconds must be a positive integer")
        if args.solver != "CBC" and args.solver != "SCIP" and args.solver != "GUROBI" and args.solver != "HIGHS" and args.solver != "all":
            raise argparse.ArgumentError(None, "The solver argument must be: CBC, SCIP, GUROBI or HIGHS or all")
        if args.symmetry_breaking != "sb" and args.symmetry_breaking != "no_sb" and args.symmetry_breaking != "all":
            raise argparse.ArgumentError(None, "The symmetry_breaking argument must be: sb, no_sb")


    if args.approach != 'all':
        print("Solving with", args.approach)
        solver.solve()

if __name__ == '__main__':
    main()
