from dagster import load_assets_from_package_module

from . import ml, temporary, tutorial

ml_assets = load_assets_from_package_module(
    package_module=ml, key_prefix="ml", group_name="MachineLearningGroup"
)


temporary_assets = load_assets_from_package_module(
    package_module=temporary, key_prefix="temp", group_name="TemporaryGroup"
)

tutorial_assets = load_assets_from_package_module(
    package_module=tutorial, key_prefix="tut", group_name="TutorialGroup"
)
