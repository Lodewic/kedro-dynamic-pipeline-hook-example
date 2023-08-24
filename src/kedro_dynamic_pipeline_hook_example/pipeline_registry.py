"""Project dynamic pipelines."""
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline

from kedro_dynamic_pipeline_hook_example.pipeline import (
    create_namespaced_model_pipeline,
    create_split_data_pipeline,
)


def register_pipelines():
    """Method that will be assigned to the callable returned by register_dynamic_pipelines(...), by a Hook."""

    raise NotImplementedError("""
    register_pipelines() is expected to be overwritten by ProjectHooks.
    Make sure the hooks is found in hooks.py and enabled in settings.py
    """)


def register_dynamic_pipelines(catalog: DataCatalog) -> dict[str, Pipeline]:
    """Register the project's pipelines depending on the catalog.

    Create pipelines dynamically based on parameters and datasets defined in the catalog.
    The function must return a callable without any arguments that will replace the
    `register_pipelines()` method in this same module, using an `after_catalog_created_hook`.

    Args:
        catalog: The DataCatalog loaded from the KedroContext.

    Returns:
        A callable that returns a mapping from pipeline names to ``Pipeline`` objects.
    """
    # create pipelines with access to catalog
    split_data_pipe = create_split_data_pipeline()
    model_pipe = create_namespaced_model_pipeline(catalog=catalog)

    def register_pipelines():
        """Register the project's pipelines.

        Returns:
            A mapping from pipeline names to ``Pipeline`` objects.
        """
        pipelines = {
            "split_data": split_data_pipe,
            "models": model_pipe,
            "__default__": split_data_pipe + model_pipe
        }

        return pipelines

    return register_pipelines
