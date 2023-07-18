FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update

RUN apt-get install -y python3

RUN pip install -r requirements.txt

COPY ./ ./

ENTRYPOINT ["python3","app.py"]