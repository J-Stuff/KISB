FROM python:3.11-slim


COPY ./src /worker
COPY ./requirements.txt /worker/requirements.txt
WORKDIR /worker

RUN pip install -r /worker/requirements.txt

CMD ["python", "main.py"]