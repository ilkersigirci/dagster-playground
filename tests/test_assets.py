from dagster import materialize

from dagster_playground.assets.tutorial.cereal import (
    cereal_protein_fractions,
    cereals,
    highest_protein_nabisco_cereal,
    nabisco_cereals,
)


def test_cereal_assets():
    assets = [
        nabisco_cereals,
        cereals,
        cereal_protein_fractions,
        highest_protein_nabisco_cereal,
    ]

    result = materialize(assets)
    assert result.success
    assert result.output_for_node("highest_protein_nabisco_cereal") == "100% Bran"
