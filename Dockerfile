# Use the MiniZinc image as the base to support MiniZinc natively
FROM minizinc/minizinc:latest AS base

# Install dependencies for building Python 3.11 from source
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
       wget \
       build-essential \
       zlib1g-dev \
       libssl-dev \
       libncurses-dev \
       libffi-dev \
       libsqlite3-dev \
       libreadline-dev \
       libbz2-dev \
       libgdbm-dev \
       liblzma-dev \
       uuid-dev \
       p7zip-full \
       zip \
       ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.11 from source
ARG PYTHON_VERSION=3.11.0
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar -xf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations \
    && make -j $(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-${PYTHON_VERSION}*

# Set Python 3.11 as the default python
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1

# Copy and set up Gurobi and MiniZinc requirements
ARG GRB_VERSION=11.0.3
LABEL vendor="Gurobi"
LABEL version=${GRB_VERSION}

# Install Gurobi and other Python packages
RUN python -m pip install --no-cache-dir gurobipy==${GRB_VERSION}

# Copy the license file and Gurobi folder to the container (adjust paths as needed)
# Make sure the license file and Gurobi files are in the build context
ADD gurobi1103 /opt/gurobi1103

# Copy and install Python dependencies from requirements.txt
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN yes Y | pysmt-install --cvc5

# Copy input files and scripts into the container
COPY /input /input
COPY . .

# Set the default command, but allow overriding with docker run
# CMD ["python", "MIP.py", "2", "GUROBI"]

