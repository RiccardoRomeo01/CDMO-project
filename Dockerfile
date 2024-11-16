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
       libgmp-dev \
       autoconf \
       gperf \
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

# Copy requirements early to optimize Docker layer caching
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Install Gurobi Python interface and solver dependencies
ARG GRB_VERSION=11.0.3
LABEL vendor="Gurobi"
LABEL version=${GRB_VERSION}
RUN python -m pip install --no-cache-dir gurobipy==${GRB_VERSION}

# Install pysmt solvers
RUN yes Y | pysmt-install --cvc5
RUN yes Y | pysmt-install --msat
RUN yes Y | pysmt-install --yices

# Copy Gurobi files (adjust paths as needed for the build context)
ADD gurobi1103 /opt/gurobi1103

# Optional: Set Gurobi license environment variable if needed
ENV /MIPMOD/gurobi.lic=/opt/gurobi1103/gurobi.lic

# Copy input files and scripts into the container
COPY /input /input
COPY . .

# Set the default command, but allow overriding with docker run
# CMD ["python", "MIP.py", "2", "GUROBI"]

