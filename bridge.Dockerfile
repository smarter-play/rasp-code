from arm32v6/alpine

RUN apk update && apk add python3 py3-pip

COPY . /code

WORKDIR /code

RUN python3 -m venv .venv

RUN pip install -r requirements.txt

ENTRYPOINT PYTHONPATH=$(pwd) python3 ./mqtt/process/rasp_process.py
