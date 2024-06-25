# pylint: disable=missing-module-docstring

import os

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from pandas import DataFrame

import mlflow
from utils.mlflow_utils import get_latest_model_from_registry

# if running locally, try to load .env file
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
load_dotenv(dotenv_path, override=True)

TRACKING_URL = os.environ.get("TRACKING_URL", "http://127.0.0.1:5001")
REGISTRY_NAME = os.environ.get("MODEL_REGISTRY_NAME", "wine_quality")

mlflow.set_tracking_uri(TRACKING_URL)

model = get_latest_model_from_registry(REGISTRY_NAME)
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


# for gunicorn in bash: gunicorn --bind 0.0.0.0:9696 app:app
# curl -X POST "http://0.0.0.0:9696/predict" -H "Content-Type: application/json"
# -d '{"DOLocationID":"20", "PULocationID":"10", "trip_distance":"10"}'
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
