from dagster import load_assets_from_package_module

from . import temporary, tutorial

temporary_assets = load_assets_from_package_module(
    package_module=temporary, key_prefix="test", group_name="TemporaryGroup"
)

tutorial_assets = load_assets_from_package_module(
    package_module=tutorial, key_prefix="test", group_name="TutorialGroup"
)
