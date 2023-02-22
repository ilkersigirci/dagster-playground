from dagster import (
    AssetKey,
    AssetsDefinition,
    GraphOut,
    OpExecutionContext,
    Out,
    Output,
    asset,
    graph,
    op,
)

from dagster_playground.assets.tutorial.multi_assets import (
    simple_multi_asset,
    simple_multi_asset_with_upstream,
)


@op
def add_three(num: int) -> int:
    return num + 3


@asset
def upstream_asset() -> int:
    return 1


@graph
def middle_asset_graph(upstream_asset):
    result = add_three(upstream_asset)
    result = add_three(result)

    return result


# NOTE: Variable name should be same with the name of the graph ?
middle_asset_graph = AssetsDefinition.from_graph(middle_asset_graph)


@asset
def downstream_asset(middle_asset_graph):
    return middle_asset_graph + 1


@graph(out={"first_asset_graph": GraphOut(), "second_asset_graph": GraphOut()})
def two_assets_graph():
    one, two = simple_multi_asset()

    return {"first_asset_graph": one, "second_asset_graph": two}


@graph(
    out={
        "first_asset_graph_upstream": GraphOut(),
        "second_asset_graph_upstream": GraphOut(),
    }
)
def two_assets_graph_upstream(upstream_asset: int):
    one, two = simple_multi_asset_with_upstream(upstream_asset)

    return {"first_asset_graph_upstream": one, "second_asset_graph_upstream": two}


two_assets_graph_asset = AssetsDefinition.from_graph(two_assets_graph)
two_assets_graph_upstream = AssetsDefinition.from_graph(two_assets_graph_upstream)

#############################################################################


@graph(out={"one": GraphOut(), "two": GraphOut()})
def return_one_and_two(zero):
    one, two = simple_multi_asset_with_upstream(zero)

    return {"one": one, "two": two}


explicit_deps_graph_asset = AssetsDefinition.from_graph(
    return_one_and_two,
    keys_by_input_name={"zero": AssetKey("upstream_asset")},
    keys_by_output_name={
        "one": AssetKey("asset_one"),
        "two": AssetKey("asset_two"),
    },
)

#############################################################################


@op(out={"foo_1": Out(is_required=False), "foo_2": Out(is_required=False)})
def subset_op(context: OpExecutionContext, bar_1):
    # Selectively returns outputs based on selected assets
    if "foo_1" in context.selected_output_names:
        yield Output(bar_1 + 1, output_name="foo_1")
    if "foo_2" in context.selected_output_names:
        yield Output(bar_1 + 2, output_name="foo_2")


@op(out={"bar_1": Out(), "bar_2": Out()})
def bar():
    return 1, 2


@op
def baz(foo_2, bar_2):
    return foo_2 + bar_2


@graph(out={"foo_asset": GraphOut(), "baz_asset": GraphOut()})
def subset_graph():
    bar_1, bar_2 = bar()
    foo_1, foo_2 = subset_op(bar_1)
    return {"foo_asset": foo_1, "baz_asset": baz(foo_2, bar_2)}


subset_graph = AssetsDefinition.from_graph(subset_graph, can_subset=True)
