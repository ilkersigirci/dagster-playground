"""
TODO:
- Convert dataclass to yaml with omegaconf and feed them to dagster with"
    `dagster job execute --config my_config.yaml`
-
"""

from dataclasses import asdict

from dagster import OpExecutionContext, config_mapping, job, op
from pydantic.dataclasses import dataclass

from dagster_playground.utils.utils import get_dataclass_asdict

##################################### Dataclass ########################################


@dataclass
class MyConfig:
    int_param: int = 2
    str_param: str = "dataclass_stuff"
    bool_param: bool = True


#################################### Hard Coded ########################################


# @op(config_schema={"str_param": str})
@op(
    config_schema=get_dataclass_asdict(
        MyConfig, return_default=False, selected_fields=["str_param"]
    )
)
def do_something(context: OpExecutionContext):
    context.log.info("str_param: " + context.op_config["str_param"])


default_config = {"ops": {"do_something": {"config": {"str_param": "stuff"}}}}


@job(config=default_config)
def hardcoded_config_job():
    do_something()


################################# Config mapping #######################################


@config_mapping(config_schema={"simplified_param": str})
def simplified_config(val):
    return {"ops": {"do_something": {"config": {"str_param": val["simplified_param"]}}}}


@job(config=simplified_config)
def config_mapping_job():
    do_something()


if __name__ == "__main__":
    dataclass_config = MyConfig()
    dataclass_config_dict = asdict(dataclass_config)

    default_config["ops"]["do_something"]["config"] = dataclass_config_dict

    hardcoded_config_job.execute_in_process()
    config_mapping_job.execute_in_process(run_config={"simplified_param": "stuff"})
