import random

from dagster import OpExecutionContext, Out, Output, graph, op


@op(out={"branch_1": Out(is_required=False), "branch_2": Out(is_required=False)})
def branching_op():
    num = random.randint(0, 1)
    if num == 0:
        yield Output(1, "branch_1")
    else:
        yield Output(2, "branch_2")


@op
def branch_1_op(context: OpExecutionContext, my_input: int):
    context.log.info(f"branch 1 input is {my_input}")


@op
def branch_2_op(context: OpExecutionContext, my_input: int):
    context.log.info(f"branch 2 input is {my_input}")


@graph
def branching():
    """Branching graph.

    NOTE: Op execution is skipped for ops that have unresolved inputs."""
    branch_1, branch_2 = branching_op()
    branch_1_op(branch_1)
    branch_2_op(branch_2)


if __name__ == "__main__":
    result = branching.execute_in_process()

    assert result.success
