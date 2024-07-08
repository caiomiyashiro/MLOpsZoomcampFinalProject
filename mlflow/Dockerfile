FROM python:3.9.7-slim

RUN pip install update pip
RUN apt-get update
# RUN apt-get install -y build-essential
RUN apt-get install -y postgresql-client

WORKDIR /app_root

COPY ["requirements.txt", "./"]
RUN pip install  -r requirements.txt

# Ensure the directory exists and has the right permissions
# RUN mkdir -p app_root/mlflow_data && chmod 777 app_root/mlflow_data

EXPOSE 5001

ENTRYPOINT mlflow server \
            --host=0.0.0.0 \
            --port=5001 \
            --backend-store-uri=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}
