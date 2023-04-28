from typing import Optional

from dagster import Config, RunConfig, asset, materialize_to_memory
from pydantic import Field

from dagster_playground.resources.pythonic_resource import CredentialsResource


class MyAssetConfig(Config):
    simple_default_value: str = "default_string"
    int_validation: int = Field(default=31, gt=0, lt=100, description="Description 0")
    simple_none: Optional[str] = None
    none_field: Optional[str] = Field(default=None, description="Description 1")
    # NOTE: `...` indicates that the field is required and has no default value.
    required_field: str = Field(default=..., description="Description 2")
    # NOTE: Specify a field that can take a  None value while still being required
    required_none_field: Optional[str] = Field(default=..., description="Description 3")


@asset
def pythonic_asset(config: MyAssetConfig) -> str:
    assert config.simple_none is None

    return f"Hello {config.simple_default_value}"


@asset
def pythonic_asset_with_resource(
    config: MyAssetConfig, cred_store_local: CredentialsResource
) -> str:
    return f"Hello {config.simple_default_value} with user: {cred_store_local.username}"


if __name__ == "__main__":
    my_config = MyAssetConfig(
        simple_default_value="Default value",
        int_validation=26,
        required_field="Required field",
        # required_none_field=None,  # FIXME: Not working
        required_none_field="Required None field",
    )

    result = materialize_to_memory(
        assets=[pythonic_asset, pythonic_asset_with_resource],
        run_config=RunConfig(
            ops={
                "pythonic_asset": my_config,
                "pythonic_asset_with_resource": my_config,
            },
        ),
        resources={"cred_store_local": CredentialsResource(username="local_user")},
    )

    print(result.output_for_node("pythonic_asset"))  # noqa: T201
    print(result.output_for_node("pythonic_asset_with_resource"))  # noqa: T201
