import random

from dagster import Output, asset


@asset(output_required=False)
def may_not_materialize():
    # to simulate an asset that may not always materialize.
    CONDITION_NUMBER = 5

    random.seed()
    if random.randint(1, 10) < CONDITION_NUMBER:
        yield Output([1, 2, 3, 4])


@asset
def downstream(may_not_materialize):
    # will not run when may_not_materialize doesn't materialize the asset
    return [*may_not_materialize, 5]
