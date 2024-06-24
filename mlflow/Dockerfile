FROM python:3.9.7-slim

RUN pip install update pip
RUN apt-get update
# RUN apt-get install -y build-essential
RUN apt-get install -y postgresql-client

WORKDIR /app_root

COPY ["requirements.txt", "./"]
RUN pip install  -r requirements.txt

EXPOSE 5001
