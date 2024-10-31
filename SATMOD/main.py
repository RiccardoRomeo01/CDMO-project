import argparse
from utils import load_data
from SAT.solver import SATsolver

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-n", "--num_instance",
                        help="Select the instance that you want to solve, with 0 we will solve all instances",
                        default=0, type= int)
    
    parser.add_argument("-i", "--input_dir",
                        help="Directory where the instance .dat files are stored",
                        default="./input", type= str)
    
    parser.add_argument("-o", "--output_dir",
                        help="Directory where the output will be saved", 
                        default="./res", type= str)
    
    parser.add_argument("-t", "--timeout", help="Timeout in seconds", default=300, type= int)
    
    parser.add_argument("-s", "--strategy", help="Search strategy", default="all", type= str)
    
    parser.add_argument("-b", "--symmetry_breaking", help="Symmetry breaking flag", default="sb", type=str)
    
    parser.add_argument("-e", "--encoding", help="Encoding to use", default="all", type= str)
    
    parser.add_argument("-f", "--fair_division", help="Impose or not a fair load division between the couriers", default="all", type= str)
    
    
    args = parser.parse_args()
    print(args)
    
    
    # Error printing
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
    
    
    # dowloading the instances data from the directory
    print("We load the instances.")
    input_data = load_data(args.input_dir, args.num_instance)
    print("Loaded!")
    
    
    # Instantiating the SAT solver
    solver = SATsolver(
        input_data = input_data,
        timeout = int(args.timeout),
        encoding = args.encoding,
        output_path = args.output_dir,
        strategy= args.strategy,
        symmetry_breaking = args.symmetry_breaking,
        fair_division = args.fair_division
    )
    
    # Starting with the solver
    print("Solving with SAT solver")
    solver.solve()


if __name__ == '__main__':
    main()