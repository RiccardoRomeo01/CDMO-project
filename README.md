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

<li> <code> -a approach, --approach approach</code> with approach = {cp, sat, smt, mip}. Selects the approach to use. 
<li> <code> -sv solver, --solver solver</code> This option is only availabel for SMT and MIP. SMT with solvers = {z3, msat, yices, cvc5}. MIP with solvers = {CBC, SCIP, HIGHS, GUROBI} for MIP. Default is "all" that resolve with all solvers.
<li> <code> -n N, --num_instance N </code> Select an instance between 1 and 21; default = 1. To solve all the instances write 0.
<li> <code> -s strategy, --strategy strategy </code> This option is possible with SAT and SMT. For both the option are = {linear, binary}. Default is "all" that it means that resolve with both.
<li> <code> -b sym_break, --symmetry_breacking sym_break </code> Use {sb, no_sb}, with "sb" you put symmetry_breacking to True and "no_sb" you put symmetry_breacking to False.
<li> <code> -e encoding, --encoding encoding </code> You can choose from {np, seq, bw, he, pb}. np = naive pair wise, seq = sequential encoding, bw = bit wise, he = heule, pb = pseudo boolean (z3 native). Default = all.
<li> <code> -f fair_division, --fair_division fair_division </code> This is a flag that can be {fair, no_fair}, depending if you want to use this constraint use "fair" or "no_fair" in the other case. Default = all.
<li> <code> -i path, --input_dir path </code> Specify the path from where take the input files, default = "./input"
<li> <code> -o path, --output_dir path</code> Specify the path in which the results will be generated, default = " ./output"
<li> <code> -t T, --timeout T</code> Set the timeout in T seconds, default = 300s.

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
