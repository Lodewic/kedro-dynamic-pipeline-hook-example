import logging
from typing import Any, Dict, Tuple

import pandas as pd
from kedro.utils import load_obj


def split_data(
    data: pd.DataFrame, parameters: Dict[str, Any]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Splits data into features and target training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters.yml.
    Returns:
        Split data.
    """

    data_train = data.sample(
        frac=parameters["train_fraction"], random_state=parameters["random_state"]
    )
    data_test = data.drop(data_train.index)

    X_train = data_train.drop(columns=parameters["target_column"])
    X_test = data_test.drop(columns=parameters["target_column"])
    y_train = data_train[parameters["target_column"]]
    y_test = data_test[parameters["target_column"]]

    return X_train, X_test, y_train, y_test

def fit_model(X: pd.DataFrame, y: pd.Series, model_type: str, model_kwargs: dict[str, Any] = {}):
    """Loads model class from `model_type` and fits model to X and y data."""
    model_class = load_obj(model_type)
    model_obj = model_class(**model_kwargs)
    model_obj.fit(X, y)
    return model_obj

def score_model(X: pd.DataFrame, y: pd.Series, model):
    """Score model on X and y dataset, assuming model has a .score(X, y) method."""
    score = model.score(X, y)
    logger = logging.getLogger(__name__)
    logger.info(f"{model=} has score of %.3f.", score)
    return score
