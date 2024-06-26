# pylint: disable=missing-module-docstring

import os
import threading

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from pandas import DataFrame

import mlflow
from utils.mlflow_utils import get_latest_model_from_registry
from utils.prometheus_utils import background_metrics_collector

# if running locally, try to load .env file
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
load_dotenv(dotenv_path, override=True)

TRACKING_URL = os.environ.get("TRACKING_URL", "http://127.0.0.1:5001")
REGISTRY_NAME = os.environ.get("MODEL_REGISTRY_NAME", "wine_quality")

mlflow.set_tracking_uri(TRACKING_URL)

model = get_latest_model_from_registry(REGISTRY_NAME)

print("Starting the thread....")
metrics_thread = threading.Thread(target=background_metrics_collector)
metrics_thread.daemon = True
metrics_thread.start()
print("Thread started...")

app = Flask("duration-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """ "
    Predict the duration of the ride
    """
    request_input = request.get_json()
    pred = model.predict(DataFrame([request_input]))

    result = {"score": pred[0]}
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
