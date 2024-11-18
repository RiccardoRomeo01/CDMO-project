# Multiple couriers planning problem
Project of "Combinatorial Decision Making and Optimization".
<br><br>
The goal of MCP is to decide for each courier the items
to be distributed and plan a tour.

In this repository you can find four solution for this problem which use four different approaches:
<li> Constraint Programming (CP)
<li> SAT 
<li> Satisfiability Modulo Theory (SMT)
<li>Mixed Integer Linear Programming (LP)

## Installation
To install all the requirements run: <br>
<code> pip install -r requirements.txt </code>

The suggested version of python is 3.10

## Execution
All the solvers can be used by running the file main.py with the command python main.py and the following arguments:

<li> <code>-a approach, --approach approach</code> with approach = {cp, sat, smt, lp, smtlib}. Selects the approach to use. 
<li> <code>-m model, --model model</code> with model = {0,1}. Select the model to use for the choosen approach, default = 1
<li><code> -n N, --num_instance N </code> Select an instance between 1 and 21; the code will execute the solver choosen from instance 1 to the given instance,
default = 0 means solve all.

<li> <code> -i path, --input_dir path </code> Specify the path from where take the input files, default = "./input"

<li> <code>-o path, --output_dir path</code> Specify the path in which the results will be generated, default = " ./output"

<li><code>-t T, --timeout T</code> Set the timeout in T seconds, default = 300s.

### Execution SMTLIB
For the executing an SMT model using different solvers is needed a Linux Enviroment and the installation of the solvers that you want to use.<br>
If you want to install z3-solver:<br>

<code>sudo apt-get install -y z3</code> <br>

If you want to install cvc4-solver: <br>

<code>sudo apt-get install -y cvc4</code> <br>

## Execution on Docker
First of all is needed to install docker: https://www.docker.com/products/docker-desktop/ <br>
**Important**: <br>
On docker there are the execution of model with the best performance for each approach.<br>

To run with docker, is needed to build the docker image: <br>
<code>docker build. -t name_image</code> <br>
name_image is the name of image that you create
<br>

After that it is possible to run the container <br>
<code>docker run -v name_folder:/project/output name_image </code> <br>
name_folder is the name of the folder where the results will be saved<br>

If the image is available, you need to load it on docker:<br>
<code>docker load -i name_image.tar</code> <br>
After that you can run the container using the previous command.

**Notes:**<br> 
To make the execution of docker linear, each approach use the instance which do not cause problem of memory exceeding, because if during the execution on docker there are problem of memory, docker kills the process and stops the execution. <br>
Obviusly for the instance which are not taken in account during the execution of the model, the solution is _UNKNOWN_.<br>
If you run the project in local(using for i.e Windows System), the problem of memory exceeding is handle without killed the process, the solution will be written but it still _UNKNOWN_.

## Best Models
In the following there are the best models for each approach:
<li> CP: <i>Circuit Model</i>, it can be run with the option: <code> -a cp -m 1</code>
<li> SAT: <i>Single Matrix</i>, it can be run with the option: <code> -a sat -m 1</code>
<li> SMT: <i>Asg Array Theory</i>, it can be run with the option: <code> -a smt -m 0</code>
<li> MIP: <i>Single Matrix Mip</i>, it can be run with the option: <code> -a lp -m 1</code>
<li> SMTLIB: it runs always the best SMT model, this approach is used only to compare different solvers on SMT 
  
## Authors
  - [Lorenzo Cassano](https://github.com/LorenzoCassano) 
  - [Jacopo D'Abramo](https://github.com/jacopodabramo)
  - [Kilian Tiziano Le Creurer](https://github.com/Kilian36) 
