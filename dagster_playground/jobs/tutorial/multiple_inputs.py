from dagster import DependencyDefinition, GraphDefinition, get_dagster_logger, graph, op


@op
def return_two() -> int:
    get_dagster_logger().info("Test manually created dagster logger")

    return 2


@op
def add_two(context, number: int):
    return number + 2


@op
def adder(context, a: int, b: int) -> int:
    return a + b


@graph
def inputs_and_outputs():
    value = return_two()
    a = add_two(value)
    b = add_two(value)
    adder(a, b)


# NOTE: Alternative way to define a graph.
two_plus_two_from_constructor = GraphDefinition(
    name="two_plus_two_from_constructor",
    node_defs=[return_two, add_two],
    dependencies={"add_two": {"number": DependencyDefinition("return_two")}},
)


if __name__ == "__main__":
    result = inputs_and_outputs.execute_in_process()
