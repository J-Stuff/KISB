FROM python:3.11-slim

# Lets KISB know its running in a docker environment. Mainly used to change datastore location
ENV IS_DOCKER=true 

# Force KISB to use the NZ timezone
ENV TZ=Pacific/Auckland

COPY ./src /worker
COPY ./requirements.txt /worker/requirements.txt
WORKDIR /worker

RUN pip install -r /worker/requirements.txt

CMD ["python", "main.py"]