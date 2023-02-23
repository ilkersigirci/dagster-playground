from typing import Tuple

from dagster import AssetKey, AssetOut, OpExecutionContext, Output, multi_asset


@multi_asset(
    outs={
        "simple_int_multi_asset": AssetOut(),
        "simple_str_multi_asset": AssetOut(),
    }
)
def simple_multi_asset() -> Tuple[int, str]:
    return 123, "abc"


# TODO: Remove later since it is redundant.
@multi_asset(
    outs={
        "simple_int_multi_asset_upstream": AssetOut(),
        "simple_str_multi_asset_upstream": AssetOut(),
    }
)
def simple_multi_asset_with_upstream(upstream_asset: int) -> Tuple[int, str]:
    return (upstream_asset, "abc")


@multi_asset(
    outs={
        "a": AssetOut(is_required=False),
        "b": AssetOut(is_required=False),
    },
    can_subset=True,
)
def split_actions(context: OpExecutionContext):
    if "a" in context.selected_output_names:
        yield Output(value=123, output_name="a")
    if "b" in context.selected_output_names:
        yield Output(value=456, output_name="b")


@multi_asset(
    outs={"c": AssetOut(), "d": AssetOut()},
    internal_asset_deps={
        "c": {AssetKey("a")},
        "d": {AssetKey("b")},
    },
)
def subset_deps_multi_asset(a, b):
    # c only depends on a
    yield Output(value=a + 1, output_name="c")

    # d only depends on b
    yield Output(value=b + 1, output_name="d")
