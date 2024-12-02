# Multiple Couriers Planning Problem
In this repository there is the solution of "Combinatorial Decision Making & Optimization" exam carried out as a group work at the University of Bologna by Mattia Buzzoni, Mirko Mornelli and Riccardo Romeo.

The goal of the Multiple Couriers Planning Problem (MCPP) is to assign items to couriers and plan their tours accordingly. Couriers must distribute all items without exceeding their load capacity.

In this repository, you will find four solutions to this problem, each utilizing a different approach:
- Constraint Programming (CP) implemented using MiniZinc
- SATisfiability (SAT) using Z3 python library
- Satisfiability Modulo Theory (SMT) realized using the solver independent python library pySMT
- Mixed Integer Linear Programming (LP) deployed through Google OR-Tools

## Installation
To install all the requirements run:
```
pip install -r requirements.txt
```

## Execution
All the solvers can be used by running the file main.py with the command ``` python main.py [arguments] ``` with the following arguments:

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

**Examples of execution lines**:
```
python main.py -a mip -n 1 -sv SCIP -b sb
```
```
python main.py -a sat -n 4 -t 300 -s binary -e he -f fair -b sb
```

---
## Execution on Docker

### 1. Install Docker
Before proceeding, you need to install Docker on your machine. You can download Docker Desktop from the official website [here](https://www.docker.com/products/docker-desktop/).

### 2. Build the Docker Image
Once Docker is installed, you'll need to build a custom Docker image for your project. To do this, follow these steps:
- Navigate to your project directory where the Dockerfile is located.
- Build the Docker image by running the following command:
  ```
  docker build -t name_image .
  ```
  - `name_image` is the name you want to give to your Docker image. The `.` refers to the current directory, where Docker will look for the Dockerfile to build the image.

> [!WARNING]
> **GUROBI solver** (which is used for MIP part) requires a valid license, and the license is not valid of the solver is running on another machine. This is why you need to run the solver in a Docker container where the license is valid. Follow the steps below to properly configure the container

### 3. Run the Docker Container
Once the image is built, you can run it as a container. This will execute the project inside the container.
- To start the container, use the following command:
  ```
  docker run name_image command
  ```
  - Replace `command` with the actual Python comman that start the project (e.g. `python main.py`)

### 4. Removing old results
To avoid overwriting old results, you may want to delete the `/res` folder before running the container again.
- Start a temporary container in interactive mode:
  ```
  docker run -it --name temp-container cdmo /bin/bash
  ```
- Delete the `/res` folder:
  ```
  rm -rf /res
  ```

### 5. Retrieve results from the container
After running the container, you may want to retrieve the resutls saved inside the container. 
- Find the name of the container: use the following command to list all containers, both running and stopped, and find the `container_name` of the one you just ran:
  ```
  docker ps -a
  ```
- Copy the results folder to your local machine: to retrieve the results stored in the <code>/res</code> folder inside the container, use the command:
  ```
  docker cp container_name:/res local_path
  ```
  - Replace `local_path` with the path on your local machine where you want to save the results.

### 6. Loading a Docker image (If you want to use GUROBI solver)
To obtain the Docker image already created without the needed to build it, you have to pull the image from the Docker hub with this code:
```
sudo docker pull mattibuzzo/cdmo-project:latest
```
>[!WARNING]
>To run this image the name to keep in mind is the entire `mattibuzzo/cdmo-project`.

---
## Authors
  - [Mattia Buzzoni](https://github.com/mattibuzzo13) 
  - [Mirko Mornelli](https://github.com/mirkomornelli)
  - [Riccardo Romeo](https://github.com/RiccardoRomeo01) 
