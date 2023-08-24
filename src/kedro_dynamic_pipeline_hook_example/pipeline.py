"""
This is a boilerplate pipeline
generated using Kedro 0.18.12
"""
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import fit_model, score_model, split_data


def create_split_data_pipeline() -> Pipeline:
    return pipeline(
        [
            node(
                func=split_data,
                inputs=["example_iris_data", "parameters"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split",
            )
        ]
    )

def create_namespaced_model_pipeline(catalog: DataCatalog) -> Pipeline:
    """Create model fit + score pipelines for all models listed under params:models.

    Parameters per model are expected to have this format,
    ```
    model_name:
      class: package.module.ModelClass
      model_kwargs:
        kwarg1: value1
        kwarg2: value2
        ...
    ```

    Where model_name.class should be an importable python location.
    """
    parameters = catalog.datasets.parameters.load()
    models = parameters["models"]  # a dictionary with the keys being the model labels

    # static inputs are re-used across all pipelines regardless of namespaces
    static_inputs = {
        "X_train": "X_train",
        "X_test": "X_test",
        "y_train": "y_train",
        "y_test": "y_test",
    }

    # Create re-usable pipeline
    model_pipe = pipeline(
        [
            node(
                func=fit_model,
                inputs=["X_train", "y_train", "params:class", "params:model_kwargs"],
                outputs="fitted_model"
            ),
            node(
                func=score_model,
                inputs=["X_test", "y_test", "fitted_model"],
                outputs="model_score"
            )
        ]
    )

    # create namespaced pipeline for each model | adds a '{model}' prefix to inputs and outputs
    namespaced_pipelines = [
        pipeline(
            pipe=model_pipe,
            namespace=model,
            inputs=static_inputs
        )
        for model in models.keys()
    ]

    # wrap entire thing in another `models` namespace, to make use of the 'models'
    # prefix in our parameters and catalog
    output_pipeline = pipeline(
        pipe=sum(namespaced_pipelines),
        namespace="models",
        inputs=static_inputs
    )
    return output_pipeline
