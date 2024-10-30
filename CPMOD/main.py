import argparse

from cp.solver import CPsolver
#from sat.src.solver import SATsolver
#from smt.src.solver import SMTsolver
#from smt.src.smtlib_solver import SMTLIBsolver
#from lp.src.solver import MIPsolver
from utils import load_data


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--approach", help="Select a modelling appraoch between cp sat, smt lp and smtlib",
                        default="cp", type=str)

    parser.add_argument("-m", "--model", help="Select a model for the solver choosen, look for additional information in the cp folder ",
                        default=1, type=int)

    parser.add_argument("-n", "--num_instance",
                        help="Select the instance that you want to solve, default = 0 solve all",
                        default=0, type=int)

    parser.add_argument("-i", "--input_dir",
                        help="Directory where the instance txt files can be found",
                        default="./input", type=str)

    parser.add_argument("-o", "--output_dir",
                        help="Directory where the output will be saved", default="./output")

    parser.add_argument("-t", "--timeout", help="Timeout in seconds", default=300)


    args = parser.parse_args()
    print(args)

    print("Loading instances")
    data = load_data(args.input_dir, args.num_instance)
    if args.approach == "cp":
        solver = CPsolver(
            data=data, 
            output_dir=args.output_dir, 
            timeout=int(args.timeout), 
            model=args.model
        )
    else:
        raise argparse.ArgumentError(None, "Please select a solver between cp, sat, smt lp and smtlib")

    '''
    elif args.approach == "sat":
        solver = SATsolver(
            data=data, 
            output_dir=args.output_dir,
            timeout=int(args.timeout),
            model=args.model
        )
    elif args.approach == "smt":
        solver = SMTsolver(
            data=data,
            output_dir=args.output_dir,
            timeout=int(args.timeout),
            model=args.model
        )
    
    elif args.approach == "smtlib":
        solver = SMTLIBsolver(
            data=data,
            output_dir=args.output_dir,
            timeout=int(args.timeout)
            )

    elif args.approach == "lp":
        solver = MIPsolver(
            data=data,
            output_dir=args.output_dir,
            timeout=int(args.timeout),
            model=args.model)
    '''
    
    print("Solving with", args.approach)
    solver.solve()


if __name__ == '__main__':
    main()
