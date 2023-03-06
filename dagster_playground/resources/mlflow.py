from dagster_mlflow import mlflow_tracking

mlflow_resource = mlflow_tracking.configured(
    {
        "experiment_name": "my_experiment",
        "mlflow_tracking_uri": "http://localhost:5000",
        ## if want to run a nested run, provide parent_run_id
        # "parent_run_id": "an_existing_mlflow_run_id",
        ## env variables to pass to mlflow
        # "env": {
        #     "MLFLOW_S3_ENDPOINT_URL": "my_s3_endpoint",
        #     "AWS_ACCESS_KEY_ID": "my_aws_key_id",
        #     "AWS_SECRET_ACCESS_KEY": "my_secret",
        # },
        ## env variables you want to log as mlflow tags
        # "env_to_tag": ["DOCKER_IMAGE_TAG"],
        ## key-value tags to add to your experiment
        # "extra_tags": {"super": "experiment"},
    }
)
