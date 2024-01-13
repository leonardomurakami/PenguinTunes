FROM python:3.10.13-slim

ARG TOKEN
ARG LAVALINK_SERVER_PASSWORD

ENV TOKEN=${TOKEN}
ENV LAVALINK_SERVER_PASSWORD=${LAVALINK_SERVER_PASSWORD}

COPY . .

RUN apt update && apt install -y git
RUN pip install discord wavelink git+https://github.com/InterStella0/starlight-dpy

ENTRYPOINT ["python", "main.py"]
