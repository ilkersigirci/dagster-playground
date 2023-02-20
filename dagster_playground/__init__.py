"""Dagster playground package."""
import pkg_resources  # type: ignore
from dagster import Definitions

from .assets import ml_assets, temporary_assets, tutorial_assets
from .jobs.bmi.config import bmi_local
from .jobs.bmi.schedules import bmi_local_schedule
from .jobs.bmi.sensors import bmi_local_s3_sensor
from .jobs.etl.config import etl_docker, etl_local
from .jobs.tutorial import (
    branching_job,
    do_it_all_with_simplified_config_job,
    fan_in_job,
    inputs_and_outputs_job,
    two_plus_two_from_constructor_job,
)

# Fetches the version of the package as defined in pyproject.toml
__version__ = pkg_resources.get_distribution("dagster_playground").version

JOBS = [
    etl_local,
    etl_docker,
    bmi_local,
    branching_job,
    do_it_all_with_simplified_config_job,
    fan_in_job,
    inputs_and_outputs_job,
    two_plus_two_from_constructor_job,
]
# JOBS = None

SCHEDULES = [bmi_local_schedule]
# SCHEDULES = None

SENSORS = [bmi_local_s3_sensor]
# SENSORS = None

ASSETS = ml_assets + temporary_assets + tutorial_assets
# ASSETS = [*temporary_assets, *tutorial_assets]
# ASSETS = None

defs = Definitions(assets=ASSETS, jobs=JOBS, schedules=SCHEDULES, sensors=SENSORS)
