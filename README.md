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

---
## Execution on Docker

### 1. Install Docker
Before proceeding, you need to install Docker on your machine. You can download Docker Desktop from the official website here: https://www.docker.com/products/docker-desktop/ <br>
**Important**: <br>
- **GUROBI solver** (which is used for MIP part) requires a valid license, and the license is not valid of the solver is running on another machine. This is why you need to run the solver in a Docker container where the license is valid. Follow the steps below to properly configure the container<br>

### 2. Build the Docker Image
Once Docker is installed, you'll need to build a custom Docker image for your project. To do this, follow these steps:
- Navigate to your project directory where the <code>Dockerfile</code> is located.
- Build the Docker image by running the following command: <code>docker build -t name_image .</code> <br>
"name_image" is the name you want to give to your Docker image. The <code>.</code> refers to the current directory, where Docker will look for the Dockerfile to build the image.

### 3. Run the Docker Container
Once the image is built, you can run it as a container. This will execute the project inside the container.
- To start the container, use the following command: <code>docker run name_image command</code> <br>
Replace "command" with the actual Python comman that start the project (e.g. <code>python main.py</code>)

### 4. Retrieve results from the container
After running the container, you may want to retrieve the resutls saved inside the container. 
- Find the name of the container: use the following command to list all containers, both running and stopped, and find the "container_name" of the one you just ran: <code>docker ps -a</code> <br>
- Copy the results folder to your local machine: to retrieve the results stored in the <code>/res</code> folder inside the container, use the <code>docker cp</code> command: <code>dockercp container_name:/res local_path</code> <br>
Replace "local_path" with the path on your local machine where you want to save the results.

### 5. Removing old results
To avoid overwriting old results, you may want to delete the <code>/res</code> folder before running the container again.
- Start a temporary container in interactive mode: <code>docker ru -it --name temp-container cdmo /bin/bash</code> <br>
- Delete the <code>/res</code> folder: inside the container, run the following command to remove the <code>/res</code> folder: <code>rm -rf /res</code> <br>

### 6. Loading a Docker image (If you want to use GUROBI solver)
If you have a Docker image saved as a <code>.tar</code> file (e.g. <code>cdmo.tar</code>), you can load it into Docker with the following command: <cpde>docker load -i cdmo.tar</code>


### 7. Decompress the Docker image
If the <code>.tar</code> file is compressed (e.g. <code>cdmo.tar.xz</code>), you will need to decompress it first. Use this command to extract the contents: <code>tar -xJvf cdmo.tar.xz</code>

---
## Authors
  - [Mattia Buzzoni](https://github.com/mattibuzzo13) 
  - [Mirko Mornelli](https://github.com/mirkomornelli)
  - [Riccardo Romeo](https://github.com/RiccardoRomeo01) 
