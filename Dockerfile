FROM jupyter/minimal-notebook:latest

WORKDIR /home/jovyan/work

RUN git clone https://github.com/brigaldies/cashflow.git

WORKDIR /home/jovyan/work/cashflow

RUN pip install -r requirements.txt

COPY cashflow-e30812754233.json cashflow-e30812754233.json

WORKDIR /home/jovyan