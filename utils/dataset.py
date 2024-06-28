# pylint: disable=invalid-name,missing-module-docstring,import-error
from typing import Tuple

import pandas as pd
from ucimlrepo import fetch_ucirepo


def get_dataset_ucirepo(repo_id: int = 186) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetches the dataset from the UCI repository and returns it as pandas dataframes.
    Parameters:
        id (int): The ID of the dataset to fetch from the UCI repository.
    Returns:
        X (pd.DataFrame): The features of the dataset.
        y (pd.DataFrame): The targets of the dataset.
    """

    # fetch dataset
    dataset = fetch_ucirepo(id=repo_id)

    # data (as pandas dataframes)
    X = dataset.data.features
    y = dataset.data.targets

    return X, y
