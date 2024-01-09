FROM python:3.10.13-slim

ARG TOKEN
ENV TOKEN=${TOKEN}

COPY . .

RUN apt update && apt install -y ffmpeg
RUN pip install nextcord pynacl yt-dlp

ENTRYPOINT ["python", "main.py"]