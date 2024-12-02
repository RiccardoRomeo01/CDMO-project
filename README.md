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
First, intall Docker on your machine. You can download Docker Desktop from the official website: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### 2. Build the Docker Image
Once Docker is installed, follow these steps to build a custom Docker image:
1. Go to your project folder, where the `Dockerfile` is located.
2. Build the Docker image by running:
  ```
  docker build -t name_image .
  ```
  - Replace `name_image` with a name for your Docker image.
  - The `.` indicates the current directory, where Docker will look for the `Dockerfile`.

> [!NOTE]
> **GUROBI** solver, used for MIP problems, requires a valid license. The license won't work if the solver is executed on another machine. Ensure the solver runs in a Docker container with the correct license configuration.

### 3. Run the Docker Container
Once the Docker image is built, you can run the project inside a container. Use this command:
  ```
  docker run name_image command
  ```
  - Replace `command` with the command to start the project, like `python main.py`

### 4. Using a Prebuilt Docker Image
>[!IMPORTANT]
>This section is essential if you want to run the GUROBI solver for MIP models.

To use the prebuilt Docker image:
1. Pull the image from Docker Hub:
```
sudo docker pull mattibuzzo/cdmo-project:latest
```
2. Use `mattibuzzo/cdmo-project` as the image name when running commands.

>[!TIP]
>You can pull the Docker Image from [Docker Hub cdmo-project](https://hub.docker.com/r/mattibuzzo/cdmo-project).

### 5. Removing old results
>[!IMPORTANT]
>This section is specific if you are using the prebuilt image.

To remove previous results, follow these steps:
1. Start a temporary container in interactive mode:
  ```
  docker run -it --name temp-container mattibuzzo/cdmo-project /bin/bash
  ```
2. Inside the container, delete the `/res` folder:
  ```
  rm -rf /res
  ```

### 6. Retrieve results from the container
After running the container, you can copy the results saved inside it to your local machine:
1. Find the container name:
  ```
  docker ps -a
  ```
  This command lists all containers, running or stopped.

2. Copy the `/res` folder from the container to your local machine:
  ```
  docker cp container_name:/res local_path
  ```
  - Replace `container_name` with the name of your container.
  - Replace `local_path` with the directory on your computer where you want to save the results.

---
## Authors
  - [Mattia Buzzoni](https://github.com/mattibuzzo13) 
  - [Mirko Mornelli](https://github.com/mirkomornelli)
  - [Riccardo Romeo](https://github.com/RiccardoRomeo01) 
