# Base image
FROM jupyter/minimal-notebook:latest

# Install curl
RUN apt-get update && apt-get install -q -y curl

WORKDIR /home/jovyan/work

# Clonet this project
RUN git clone https://github.com/brigaldies/cashflow.git

WORKDIR /home/jovyan/work/cashflow

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the AWS key file
COPY cashflow-e30812754233.json cashflow-e30812754233.json

WORKDIR /home/jovyan