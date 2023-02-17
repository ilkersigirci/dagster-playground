"""Dagster playground package."""
import pkg_resources  # type: ignore
from dagster import Definitions

from .assets import ml_assets, temporary_assets, tutorial_assets

# Fetches the version of the package as defined in pyproject.toml
__version__ = pkg_resources.get_distribution("dagster_playground").version


all_assets = ml_assets + temporary_assets + tutorial_assets
# all_assets = [*temporary_assets, *tutorial_assets]

defs = Definitions(assets=all_assets)
