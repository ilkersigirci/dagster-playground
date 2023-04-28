from dagster import Config, RunConfig, asset, materialize_to_memory
from pydantic import Field


class MyAssetConfig(Config):
    name: str = "Ilker"
    age: int = Field(42, gt=0, lt=100, description="Age of the person")
    # Here, the ellipses `...` indicates that the field is required and has no default value.
    job: str = Field(..., description="Job of the person")


@asset
def pythonic_configurable_asset(config: MyAssetConfig) -> str:
    return f"Hello {config.name}"


if __name__ == "__main__":
    result = materialize_to_memory(
        [pythonic_configurable_asset],
        run_config=RunConfig(
            {"pythonic_configurable_asset": MyAssetConfig(name="Ilker", job="Engineer")}
        ),
    )

    print(result.output_for_node("pythonic_configurable_asset"))  # noqa: T201
