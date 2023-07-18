FROM python:3

WORKDIR /app

COPY . /app


RUN pip install requirements.txt


ENTRYPOINT ["python3","app.py"]