# Multiple couriers planning problem
Project of "Combinatorial Decision Making and Optimization".
<br><br>
The goal of MCP is to decide for each courier the items
to be distributed and plan a tour.

In this repository you can find four solution for this problem which use four different approaches:
<li> Constraint Programming (CP)
<li> SAT 
<li> Satisfiability Modulo Theory (SMT)
<li> Mixed Integer Linear Programming (LP)

## Installation
To install all the requirements run: <br>
<code> pip install -r requirements.txt </code>

## Execution
All the solvers can be used by running the file main.py with the command python main.py and the following arguments:

| **Option**               | **Description**                                                                                                                                                         | **Values/Defaults**                                                                                                         |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| `-a approach`, `--approach approach` | Selects the approach to use.                                                                                                                              | `{cp, sat, smt, mip}` (Constraint Programming, SAT, SMT, Mixed Integer Programming)                                         |
| `-sv solver`, `--solver solver`      | Specify the solver to use. Available only for `SMT` and `MIP`.                                                                                            | SMT: `{z3, msat, yices, cvc5}` <br> MIP: `{CBC, SCIP, HIGHS, GUROBI}` <br> Default: `all` (solves using all solvers)         |
| `-n N`, `--num_instance N`           | Selects the instance to solve.                                                                                                                            | Values: `1` to `21` <br> Default: `1` <br> Use `0` to solve all instances.                                                 |
| `-s strategy`, `--strategy strategy` | Choose a strategy (only for `SAT` and `SMT`).                                                                                                             | `{linear, binary}` <br> Default: `all` (solves using both strategies).                                                     |
| `-b sym_break`, `--symmetry_breaking sym_break` | Enable or disable symmetry breaking.                                                                                                            | `{sb, no_sb}` <br> Default: `no_sb`.                                                                                       |
| `-e encoding`, `--encoding encoding` | Select the encoding method to use.                                                                                                                        | `{np, seq, bw, he, pb}` <br> `np`: Naive Pairwise <br> `seq`: Sequential <br> `bw`: Bitwise <br> `he`: Heule <br> `pb`: Pseudo Boolean <br> Default: `all`. |
| `-f fair_division`, `--fair_division fair_division` | Enable or disable fair division constraints.                                                                                                     | `{fair, no_fair}` <br> Default: `all`.                                                                                     |
| `-i path`, `--input_dir path`        | Specify the directory to read input files from.                                                                                                           | Default: `./input`.                                                                                                        |
| `-o path`, `--output_dir path`       | Specify the directory to save results.                                                                                                                    | Default: `./output`.                                                                                                       |
| `-t T`, `--timeout T`                | Set a timeout for solving in seconds.                                                                                                                     | Default: `300s`.                                                                                                           |

**Example of execution line**:<br>
<code>python main.py -a mip -n 1 -sv SCIP -b sb</code>


## Execution on Docker
First of all is needed to install docker: https://www.docker.com/products/docker-desktop/ <br>
**Important**: <br>
On docker there are all the model used, but it's not work if you try to use GUROBI solver with MIP because the licence there is not licence connected to the other pc, so it is possible to use this solver with the Docker image that it is explained after.<br>

To run with docker, is needed to build the docker image: <br>
<code>docker build -t name_image .</code> <br>
name_image is the name of image that you create
<br>

After that it is possible to run the container <br>
<code>docker run --rm name_image command</code> <br>
command is the python command to start the main.py as in the example as above<br>

To retrieve the folder where there are the results you have to run this command <br>
<code>docker cp name_image:/res local_path</code> <br>
/res is the folder where the results are saved on the container, local_path is the path on your computer where to save the results folder. 

If the image is available, you need to load it on docker:<br>
<code>docker load -i name_image.tar</code> <br>
After that you can run the container using the previous command.
This is the only way to use GUROBI solver for MIP, because we insert the licence on the installation.
  
## Authors
  - [Mattia Buzzoni](https://github.com/mattibuzzo13) 
  - [Mirko Mornelli](https://github.com/mirkomornelli)
  - [Riccardo Romeo](https://github.com/RiccardoRomeo01) 
