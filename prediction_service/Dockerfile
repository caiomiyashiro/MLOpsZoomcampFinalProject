FROM python:3.12.4-slim

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y

WORKDIR /app_root

COPY ["requirements.txt", "./"]
RUN pip install  -r requirements.txt

COPY ["app.py", "./"]
COPY ["sample_model.pkl", "./"]
COPY ["utils/", "./utils"]

EXPOSE 9696
