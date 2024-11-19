FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app
RUN python -m pip install --upgrade pip


COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY ./core /app  
