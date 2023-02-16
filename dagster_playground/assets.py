import csv
import random

import requests
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


@asset
def cereals():
    response = requests.get("https://docs.dagster.io/assets/cereal.csv")
    lines = response.text.split("\n")
    return list(csv.DictReader(lines))


@asset
def nabisco_cereals(cereals):
    """Cereals manufactured by Nabisco"""
    return [row for row in cereals if row["mfr"] == "N"]


@asset
def cereal_protein_fractions(cereals):
    """
    For each cereal, records its protein content as a fraction of its total mass.
    """
    result = {}
    for cereal in cereals:
        total_grams = float(cereal["weight"]) * 28.35
        result[cereal["name"]] = float(cereal["protein"]) / total_grams

    return result


@asset
def highest_protein_nabisco_cereal(nabisco_cereals, cereal_protein_fractions):
    """
    The name of the nabisco cereal that has the highest protein content.
    """
    sorted_by_protein = sorted(
        nabisco_cereals, key=lambda cereal: cereal_protein_fractions[cereal["name"]]
    )
    return sorted_by_protein[-1]["name"]
