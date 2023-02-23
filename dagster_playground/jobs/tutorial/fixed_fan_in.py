from typing import List

from dagster import OpExecutionContext, graph, op


@op
def return_one() -> int:
    return 1


@op
def sum_fan_in(context: OpExecutionContext, nums: List[int]) -> int:
    result = sum(nums)
    context.log.info(f"Result is {result}")

    return result


@graph
def fan_in():
    fan_outs = []
    for i in range(0, 5):
        # fan_outs.append(return_one())
        fan_outs.append(return_one.alias(f"return_one_{i+100}")())

    sum_fan_in(fan_outs)
