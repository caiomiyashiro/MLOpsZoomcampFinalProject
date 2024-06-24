# pylint: disable=missing-module-docstring
import pickle

import pandas as pd
from flask import Flask, jsonify, request

# optional do download model from MLFLOW
# RUN_ID = 'dafcb234fvrwv24392ik'
# MLFLOW_TRACKING_URI = 'http:127.0.0.1:5000'
# ######
# logged_model = f'runs:/{RUN_ID}/model'
# also better to download models and artifacts from storage instead of trackign server
# model = mlflow.pyfunc.load_model(logged_model)
# ######
# client = MlflowClient(tracking_uri = MLFLOW_TRACKING_URI)
# path = client.download_artifacts(run_id=RUN_ID, path='other_artifact.bin')
# with open(path, 'rb') as f:
#     other_artifact = pickle.load(f)

with open("rf_model.pickle", "rb") as f:
    model = pickle.load(f)

app = Flask("duration-prediction")


def prepare_features(ride_input):
    """ "
    Prepare features for the model
    """
    location = ride_input["PULocationID"] + "_" + ride_input["DOLocationID"]
    trip_distance = ride_input["trip_distance"]
    return pd.DataFrame({"location": [location], "trip_distance": [trip_distance]})


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """ "
    Predict the duration of the ride
    """
    ride_input = request.get_json()

    features = prepare_features(ride_input)
    pred = model.predict(features)

    result = {"duration": pred[0]}
    return jsonify(result)


# for gunicorn in bash: gunicorn --bind 0.0.0.0:9696 app:app
# curl -X POST "http://0.0.0.0:9696/predict" -H "Content-Type: application/json"
# -d '{"DOLocationID":"20", "PULocationID":"10", "trip_distance":"10"}'
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
