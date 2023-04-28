"""Example for mlflow nested runs."""
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID


def create_nested_run(experiment_name: str = "nested_experiment"):
    """Create a nested run."""

    client = MlflowClient()

    if experiment_name not in [e.name for e in client.list_experiments()]:
        experiment = client.create_experiment(experiment_name)
    else:
        experiment = client.get_experiment_by_name(experiment_name).experiment_id

    parent_run = client.create_run(experiment_id=experiment)
    client.log_param(parent_run.info.run_id, "who", "parent")

    child_run_1 = client.create_run(
        experiment_id=experiment, tags={MLFLOW_PARENT_RUN_ID: parent_run.info.run_id}
    )
    client.log_param(child_run_1.info.run_id, "who", "child 1")

    child_run_2 = client.create_run(
        experiment_id=experiment, tags={MLFLOW_PARENT_RUN_ID: parent_run.info.run_id}
    )
    client.log_param(child_run_2.info.run_id, "who", "child 2")


if __name__ == "__main__":
    create_nested_run()
