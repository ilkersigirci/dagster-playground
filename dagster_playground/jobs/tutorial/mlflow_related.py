from dagster import OpExecutionContext, job, op
from dagster_mlflow import end_mlflow_on_run_finished

from dagster_playground.resources.mlflow_related import mlflow_resource


@op(required_resource_keys={"mlflow"})
def mlflow_op(context: OpExecutionContext):
    some_params = {"some_param": "some_value", "some_other_param": "some_other_value"}
    context.resources.mlflow.log_params(some_params)

    # context.mlflow.tracking.MlflowClient().create_registered_model(some_model_name)


@end_mlflow_on_run_finished
@job(resource_defs={"mlflow": mlflow_resource})
def mlflow_job():
    mlflow_op()
