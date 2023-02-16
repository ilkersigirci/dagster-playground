"""Dagster playground package."""
import pkg_resources  # type: ignore
from dagster import Definitions, load_assets_from_modules

from . import assets

# Fetches the version of the package as defined in pyproject.toml
__version__ = pkg_resources.get_distribution("dagster_playground").version


defs = Definitions(assets=load_assets_from_modules([assets]))
