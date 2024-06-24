FROM python:3.9.7-slim

RUN pip install update pip
RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app_root

COPY ["requirements.txt", "./"]
RUN pip install  -r requirements.txt

COPY ["rf_model.pickle", "app.py", "./"]

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "app:app"]
