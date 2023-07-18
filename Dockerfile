FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip install requirements.txt

COPY ./ ./

ENTRYPOINT ["python3","app.py"]