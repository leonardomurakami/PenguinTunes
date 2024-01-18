FROM python:3.10.13-slim

RUN apt update && apt install -y git

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
