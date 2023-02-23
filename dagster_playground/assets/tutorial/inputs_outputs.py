from typing import Tuple

from dagster import Out, op


@op(out={"int_output": Out(), "str_output": Out()})
def my_multiple_output_annotation_op() -> Tuple[int, str]:
    return (5, "foo")


# NOTE: Not the same as above.
@op
def my_single_tuple_output_op() -> Tuple[int, str]:
    return (5, "foo")
