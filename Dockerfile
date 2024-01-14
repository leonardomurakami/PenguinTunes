FROM python:3.10.13-slim

COPY . .

RUN apt update && apt install -y git
RUN pip install discord wavelink git+https://github.com/InterStella0/starlight-dpy sqlalchemy pynacl

ENTRYPOINT ["python", "main.py"]
