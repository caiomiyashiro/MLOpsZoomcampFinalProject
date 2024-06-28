# pylint: disable=missing-module-docstring,import-error
import json

import numpy as np
import requests
from dataset import get_dataset_ucirepo
from pandas import DataFrame


def test_predict_endpoint(
    X: DataFrame, predict_endpoint: str = "http://127.0.0.1:9696/predict"
):
    # pylint: disable=invalid-name
    """
    Test the predict endpoint
    Parameters:
        predict_endpoint (str): The endpoint of the predict service
    """

    results = []
    max_rows = 1
    for i in range(max_rows):
        data = X.iloc[i].to_dict()
        req_data = json.dumps(data)

        headers = {"Content-Type": "application/json"}
        response_ = requests.post(
            predict_endpoint, data=req_data, headers=headers, timeout=5
        )
        results.append(response_.json()["score"])
    return results


if __name__ == "__main__":
    df, _ = get_dataset_ucirepo(repo_id=186)
    responses = test_predict_endpoint(df)
    print(np.unique(responses, return_counts=True))
