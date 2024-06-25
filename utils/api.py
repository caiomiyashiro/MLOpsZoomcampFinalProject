# pylint: disable=missing-module-docstring
import json

import requests
from dataset import get_dataset_ucirepo


def test_predict_endpoint(predict_endpoint: str = "http://127.0.0.1:9696/predict"):
    # pylint: disable=invalid-name
    """
    Test the predict endpoint
    Parameters:
        predict_endpoint (str): The endpoint of the predict service
    """

    X, _ = get_dataset_ucirepo(repo_id=186)

    data = X.iloc[0].to_dict()
    req_data = json.dumps(data)

    headers = {"Content-Type": "application/json"}
    response_ = requests.post(
        predict_endpoint, data=req_data, headers=headers, timeout=5
    )
    return response_.json()


if __name__ == "__main__":
    response = test_predict_endpoint()
    print(response)
