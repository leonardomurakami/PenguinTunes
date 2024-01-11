FROM python:3.10.13-slim

ARG TOKEN
ENV TOKEN=${TOKEN}

COPY . .

RUN pip install discord pynacl yt-dlp wavelink

ENTRYPOINT ["python", "main.py"]
