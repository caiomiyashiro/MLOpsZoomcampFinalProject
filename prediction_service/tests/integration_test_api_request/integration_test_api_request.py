# pylint: disable=missing-module-docstring,wrong-import-position
# adding parent folder to sys.path to use utils folder functions
import os
import sys

# Add the path to the 'prediction_service' directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

# Add the path to the 'tests' directory
tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(tests_dir)

import json

import requests
from dotenv import find_dotenv, load_dotenv

from utils.dataset import get_dataset_ucirepo

dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
load_dotenv(dotenv_path, override=True)


def test_predict_endpoint():
    # pylint: disable=invalid-name
    """
    Test the predict endpoint
    Parameters:
        predict_endpoint (str): The endpoint of the predict service
    """
    PREDICTION_SERVICE_URL = os.environ.get(
        "PREDICTION_SERVICE_URL", "http://127.0.0.1:9696"
    )
    print(f"------------- PREDICTION_SERVICE_URL {PREDICTION_SERVICE_URL}")

    df, _ = get_dataset_ucirepo(repo_id=186)

    data = df.iloc[0].to_dict()
    req_data = json.dumps(data)

    headers = {"Content-Type": "application/json"}
    response_ = requests.post(
        f"{PREDICTION_SERVICE_URL}/predict", data=req_data, headers=headers, timeout=5
    )
    return response_


if __name__ == "__main__":
    response = test_predict_endpoint()
    print(response.status_code)
    assert response.status_code == 200
