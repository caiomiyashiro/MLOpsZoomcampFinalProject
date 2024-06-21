# pylint: disable=invalid-name,missing-module-docstring

import os
from typing import Tuple

import mlflow
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from ucimlrepo import fetch_ucirepo

load_dotenv()  # Load variables from .env file

EXPERIMENT_NAME = os.environ.get(
    "EXPERIMENT_NAME", "wine_quality_hyperparameter_optimization_"
)
TRACKING_URL = os.environ.get("TRACKING_URL", "http://localhost:5001")

mlflow.set_tracking_uri(TRACKING_URL)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.sklearn.autolog()


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


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_val: pd.DataFrame,
) -> DecisionTreeRegressor:
    """
    Trains a Decision Tree model on the given features and targets.
    Parameters:
        X_train (pd.DataFrame): The features of the training set.
        y_train (pd.DataFrame): The targets of the training set.
        X_val (pd.DataFrame): The features of the validation set.
        y_val (pd.DataFrame): The targets of the validation set.
    Returns:
        final_model (DecisionTreeRegressor): The trained Decision Tree model.
    """
    # Split the data

    # Define the hyperparameter search space
    space = {
        "criterion": hp.choice(
            "criterion", ["squared_error", "friedman_mse", "absolute_error", "poisson"]
        ),
        "splitter": hp.choice("splitter", ["best", "random"]),
        "max_depth": hp.choice("max_depth", [None] + list(range(1, 21))),
        "min_samples_split": hp.choice(
            "min_samples_split", range(2, 21)
        ),  # Integer values from 2 to 20
        "min_samples_leaf": hp.choice(
            "min_samples_leaf", range(1, 21)
        ),  # Integer values from 1 to 20
        "min_weight_fraction_leaf": hp.uniform("min_weight_fraction_leaf", 0.0, 0.5),
        "max_features": hp.choice(
            "max_features", [None, "sqrt", "log2"] + list(np.arange(0.1, 1.1, 0.1))
        ),
        "max_leaf_nodes": hp.choice("max_leaf_nodes", [None] + list(range(2, 101))),
        "min_impurity_decrease": hp.uniform("min_impurity_decrease", 0.0, 1.0),
        "ccp_alpha": hp.uniform("ccp_alpha", 0.0, 1.0),
    }

    # Define the objective function
    def objective(params):
        with mlflow.start_run():
            # Create the model with the given hyperparameters
            model = DecisionTreeRegressor(**params)
            model.fit(X_train, y_train)
            y_val_pred = model.predict(X_val)
            mse = mean_squared_error(y_val, y_val_pred)
            mlflow.sklearn.log_model(model, artifact_path="artifacts")
        # Return the loss (negative score)
        return {"loss": mse * -1, "status": STATUS_OK}

    # Perform hyperparameter optimization
    trials = Trials()
    _ = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=50, trials=trials)

    # best_params = {
    #     'max_depth': int(best['max_depth']),
    #     'min_samples_split': best['min_samples_split'],
    #     'min_samples_leaf': best['min_samples_leaf']
    # }

    # # Train the final model
    # final_model = DecisionTreeRegressor(**best_params)
    # X = pd.concat([X_train, X_val])
    # y = pd.concat([y_train, y_val])
    # final_model.fit(X, y)


def main():
    # pylint: disable=missing-function-docstring
    # Fetch the dataset
    X, y = get_dataset_ucirepo()

    # Split the data
    # X_test and y_test will be used for evidently
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train the model
    train_model(X_train, y_train, X_test, y_test)


if __name__ == "__main__":
    main()
