from dagster import Config, RunConfig, asset, materialize_to_memory
from pydantic import Field

from dagster_playground.resources.pythonic_resource import CredentialsResource


class MyAssetConfig(Config):
    name: str = "Ilker"
    age: int = Field(31, gt=0, lt=100, description="Age of the person")
    # Here, the ellipses `...` indicates that the field is required and has no default value.
    job: str = Field(..., description="Job of the person")


@asset
def pythonic_asset(config: MyAssetConfig) -> str:
    return f"Hello {config.name}"


@asset
def pythonic_asset_with_resource(
    config: MyAssetConfig, cred_store_local: CredentialsResource
) -> str:
    return f"Hello {config.name} with user: {cred_store_local.username}"


if __name__ == "__main__":
    my_config = MyAssetConfig(
        name="Ilker",
        job="Engineer",
        age=26,
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
