from typing import Tuple

from dagster import (
    AssetOut,
    AssetsDefinition,
    GraphOut,
    asset,
    graph,
    multi_asset,
    op,
)


@op
def add_three(num: int) -> int:
    return num + 3


@asset
def upstream_asset() -> int:
    return 1


@multi_asset(outs={"int_output": AssetOut(), "str_output": AssetOut()})
def two_output_asset(upstream_asset: int) -> Tuple[int, str]:
    return (upstream_asset + 5, "foo")


@graph
def middle_asset_graph(upstream_asset):
    return add_three(upstream_asset)


# NOTE: Variable name should be same with the name of the graph ?
middle_asset_graph = AssetsDefinition.from_graph(middle_asset_graph)


@asset
def downstream_asset(middle_asset_graph):
    return middle_asset_graph + 1


@graph(out={"first_asset": GraphOut(), "second_asset": GraphOut()})
def two_assets_graph(upstream_asset):
    one, two = two_output_asset(upstream_asset)

    return {"first_asset": one, "second_asset": two}


two_assets = AssetsDefinition.from_graph(two_assets_graph)
