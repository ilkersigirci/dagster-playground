import argparse
import logging

import pandas as pd

from dagster_playground.assets.ml.m4 import evaluate_M4
from dagster_playground.assets.ml.m5 import evaluate_M5


def evaluate_my_model(forecasts, dataset, root_dir, train_time=None):
    assert dataset in [
        "M4-Daily",
        "M4-Yearly",
        "M4-Quarterly",
        "M4-Monthly",
        "M4-Weekly",
        "M4-Hourly",
        "M5",
    ], "Dataset {} not supported!".format(dataset)

    if "M4" in dataset:
        evaluate_M4(dataset=dataset, forecasts=forecasts, root_dir=root_dir)

    if "M5" in dataset:
        return evaluate_M5(forecasts=forecasts, root_dir=root_dir)

    return None


class TSBenchmarks:
    """Benchmarks"""

    def __init__(  # noqa: PLR0913
        self,
        dataset: str,
        filename: str,
        unique_id_column: str,
        ds_column: str,
        y_column: str,
    ) -> "TSBenchmarks":
        self.dataset = dataset
        self.filename = filename
        self.unique_id_column = unique_id_column
        self.ds_column = ds_column
        self.y_column = y_column
        self.df: pd.DataFrame

        self.df = self._read_file()

    def _read_file(self) -> pd.DataFrame:
        logger.info("Reading file...")
        input_df = pd.read_csv(f"/opt/ml/processing/input/{self.filename}")
        logger.info("File readed.")
        renamer = {
            self.unique_id_column: "unique_id",
            self.ds_column: "ds",
            self.y_column: "y",
        }

        return input_df.rename(columns=renamer)

    def benchmark(self) -> None:
        """Compute metrics"""
        logger.info("Computing metrics...")
        root_dir = "/opt/ml/processing/output/"
        model_metrics = evaluate_my_model(
            forecasts=self.df, dataset=self.dataset, root_dir=root_dir, train_time=None
        )

        model_metrics.to_csv(root_dir + "benchmarks.csv", index=False)
        logger.info("File written...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="M5")
    parser.add_argument("--filename", type=str)
    parser.add_argument("--unique-id-column", type=str, default="unique_id")
    parser.add_argument("--ds-column", type=str, default="ds")
    parser.add_argument("--y-column", type=str, default="y")

    args = parser.parse_args()

    benchmarking = TSBenchmarks(**vars(args))
    benchmarking.benchmark()
