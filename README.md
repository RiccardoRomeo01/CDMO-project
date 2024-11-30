# Multiple Couriers Planning Problem
In this repository there is the solution of "Combinatorial Decision Making & Optimization" exam carried out as a group work at the University of Bologna by Mattia Buzzoni, Mirko Mornelli and Riccardo Romeo.
<br><br>
The goal of the Multiple Couriers Planning Problem (MCPP) is to assign items to couriers and plan their tours accordingly. Couriers must distribute all items without exceeding their load capacity.

In this repository, you will find four solutions to this problem, each utilizing a different approach:
<li> Constraint Programming (CP) implemented using MiniZinc
<li> SATisfiability (SAT) using Z3 python library
<li> Satisfiability Modulo Theory (SMT) realized using the solver independent python library pySMT
<li> Mixed Integer Linear Programming (LP) deployed through Google OR-Tools

## Installation
To install all the requirements run: <br>
<code> pip install -r requirements.txt </code>

## Execution
All the solvers can be used by running the file main.py with the command <code>python main.py</code> and the following arguments:

| **Option**               | **Description**                                                                                                                                                         | **Values/Defaults**                                                                                                         |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| `-a approach`, `--approach approach` | Selects the approach to use.                                                                                                                              | `{cp, sat, smt, mip}` (Constraint Programming, SAT, SMT, Mixed Integer Programming)                                         |
| `-sv solver`, `--solver solver`      | Specifies the solver to use. Available only for `SMT` and `MIP`.                                                                                            | SMT: `{z3, msat, yices, cvc5}` <br> MIP: `{CBC, SCIP, HIGHS, GUROBI}` <br> Default: `all` (solves using all solvers)         |
| `-n N`, `--num_instance N`           | Selects the instance to solve.                                                                                                                            | Values: `1` to `21` <br> Default: `1` <br> Use `0` to solve all instances.                                                 |
| `-s strategy`, `--strategy strategy` | Chooses a strategy (only for `SAT` and `SMT`).                                                                                                             | `{linear, binary}` <br> Default: `all` (solves using both strategies).                                                     |
| `-b sym_break`, `--symmetry_breaking sym_break` | Enables or disables symmetry breaking.                                                                                                            | `{sb, no_sb}` <br> Default: `no_sb`.                                                                                       |
| `-e encoding`, `--encoding encoding` | Selects the encoding method to use.                                                                                                                        | `{np, seq, bw, he, pb}` <br> `np`: Naive Pairwise <br> `seq`: Sequential <br> `bw`: Bitwise <br> `he`: Heule <br> `pb`: Pseudo Boolean <br> Default: `all`. |
| `-f fair_division`, `--fair_division fair_division` | Enables or disables fair division constraints.                                                                                                     | `{fair, no_fair}` <br> Default: `all`.                                                                                     |
| `-i path`, `--input_dir path`        | Specifies the directory to read input files from.                                                                                                           | Default: `./input`.                                                                                                        |
| `-o path`, `--output_dir path`       | Specifies the directory to save results.                                                                                                                    | Default: `./output`.                                                                                                       |
| `-t T`, `--timeout T`                | Sets a timeout for solving in seconds.                                                                                                                     | Default: `300s`.                                                                                                           |

**Examples of execution lines**:<br>
<code>python main.py -a mip -n 1 -sv SCIP -b sb</code> <br>
<code>python main.py -a sat -n 4 -t 300 -s binary -e he -f fair -b sb</code>


## Execution on Docker
First of all is needed to install docker: https://www.docker.com/products/docker-desktop/ <br>
**Important**: <br>
On docker there are all the implemented models, but the project doesn't work if you try to use GUROBI solver with MIP because the licence is not acceptable if the solver runs on another machine, so it is possible to use this solver with the Docker image (check the following to run that).<br>

To run with docker, is needed to build the Docker image: <br>
<code>docker build -t name_image .</code> <br>
"name_image" is the name of image that you create
<br>

After that it is possible to run the container: <br>
<code>docker run --rm name_image command</code> <br>
"command" is the python command to start the main.py as in the example as above<br>

To retrieve the folder where there are the results you have to run the following command: <br>
<code>docker cp name_image:/res local_path</code> <br>
"/res" is the folder where the results are saved on the container, "local_path" is the path on your computer where to save the results folder. 

If the image is available, you need to load it on docker: <br>
<code>docker load -i name_image.tar</code> <br>
Thus, you can run the container using the previous command.
This is the only way to use GUROBI solver for MIP, because the licence is required during the solver installation.
**Important**: <br>
The <code>cdmo.tar</code> is compressed in cdmo.tar.xz. To use it, you must first decompress it using the following command: <code>tar -xJvf cdmo.tar.xz</code>
  
## Authors
  - [Mattia Buzzoni](https://github.com/mattibuzzo13) 
  - [Mirko Mornelli](https://github.com/mirkomornelli)
  - [Riccardo Romeo](https://github.com/RiccardoRomeo01) 
