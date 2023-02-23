"""Copied from https://github.com/Nixtla/nixtla/tree/main/tsbenchmarks/benchmarks

python m4.py \
--dataset M4-Daily \
--filename train/M4-forecasts-benchmark.csv \
--unique-id-column unique_id \
--ds-column ds \
--y-column y
"""
import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd

from dagster_playground.assets.ml.utils import (
    download_file,
    loss_benchmark,
    loss_per_serie,
    loss_per_timestamp,
    mase,
    smape,
)

logger = logging.getLogger(__name__)


# Cell
@dataclass
class Info:
    """
    Info Dataclass of datasets.
    Args:
        groups (Tuple): Tuple of str groups
        class_groups (Tuple): Tuple of dataclasses.
    """

    groups: Tuple[str]
    class_groups: Tuple[dataclass]

    def get_group(self, group: str):
        """Gets dataclass of group."""
        if group not in self.groups:
            raise Exception(f"Unkown group {group}")

        return self.class_groups[self.groups.index(group)]

    def __getitem__(self, group: str):
        """Gets dataclass of group."""
        if group not in self.groups:
            raise Exception(f"Unkown group {group}")

        return self.class_groups[self.groups.index(group)]

    def __iter__(self):
        for group in self.groups:
            yield group, self.get_group(group)


# Cell
@dataclass
class Yearly:
    seasonality: int = 1
    horizon: int = 6
    freq: str = "Y"
    name: str = "Yearly"
    n_ts: int = 23_000


@dataclass
class Quarterly:
    seasonality: int = 4
    horizon: int = 8
    freq: str = "Q"
    name: str = "Quarterly"
    n_ts: int = 24_000


@dataclass
class Monthly:
    seasonality: int = 12
    horizon: int = 18
    freq: str = "M"
    name: str = "Monthly"
    n_ts: int = 48_000


@dataclass
class Weekly:
    seasonality: int = 1
    horizon: int = 13
    freq: str = "W"
    name: str = "Weekly"
    n_ts: int = 359


@dataclass
class Daily:
    seasonality: int = 1
    horizon: int = 14
    freq: str = "D"
    name: str = "Daily"
    n_ts: int = 4_227


@dataclass
class Hourly:
    seasonality: int = 24
    horizon: int = 48
    freq: str = "H"
    name: str = "Hourly"
    n_ts: int = 414


@dataclass
class Other:
    seasonality: int = 1
    horizon: int = 8
    freq: str = "D"
    name: str = "Other"
    n_ts: int = 5_000
    included_groups: Tuple = ("Weekly", "Daily", "Hourly")


# Cell
M4Info = Info(
    groups=("Yearly", "Quarterly", "Monthly", "Weekly", "Daily", "Hourly", "Other"),
    class_groups=(Yearly, Quarterly, Monthly, Weekly, Daily, Hourly, Other),
)


# Cell
@dataclass
class M4:
    source_url: str = (
        "https://raw.githubusercontent.com/Mcompetitions/M4-methods/master/Dataset/"
    )
    naive2_forecast_url: str = "https://github.com/Nixtla/m4-forecasts/raw/master/forecasts/submission-Naive2.zip"

    @staticmethod
    def load(
        directory: str, group: str, cache: bool = True
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Downloads and loads M4 data.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        group: str
            Group name.
            Allowed groups: 'Yearly', 'Quarterly', 'Monthly',
                            'Weekly', 'Daily', 'Hourly'.
        cache: bool
            If `True` saves and loads

        Notes
        -----
        [1] Returns train+test sets.
        """
        path = f"{directory}/m4/datasets"
        file_cache = f"{path}/{group}.p"

        if os.path.exists(file_cache) and cache:
            df_train, df_test, X_df, S_df = pd.read_pickle(file_cache)

            return df_train, df_test, X_df, S_df

        if group == "Other":
            # Special case.
            included_dfs = [
                M4.load(directory, gr) for gr in M4Info["Other"].included_groups
            ]
            df, *_ = zip(*included_dfs)
            df = pd.concat(df)
        else:
            M4.download(directory, group)
            path = f"{directory}/m4/datasets"
            class_group = M4Info[group]
            S_df = pd.read_csv(
                f"{directory}/m4/datasets/M4-info.csv", usecols=["M4id", "category"]
            )
            S_df["category"] = S_df["category"].astype("category").cat.codes
            S_df.rename({"M4id": "unique_id"}, axis=1, inplace=True)
            S_df = S_df[S_df["unique_id"].str.startswith(class_group.name[0])]

            def read_and_melt(file):
                df = pd.read_csv(file)
                df.columns = ["unique_id", *list(range(1, df.shape[1]))]
                df = pd.melt(df, id_vars=["unique_id"], var_name="ds", value_name="y")
                df = df.dropna()

                return df

            df_train = read_and_melt(file=f"{path}/{group}-train.csv")
            df_test = read_and_melt(file=f"{path}/{group}-test.csv")

            # len_train = df_train.groupby('unique_id').agg({'ds': 'max'}).reset_index()
            # len_train.columns = ['unique_id', 'len_serie']
            # df_test = df_test.merge(len_train, on=['unique_id'])
            # df_test['ds'] = df_test['ds'] + df_test['len_serie']
            # df_test.drop('len_serie', axis=1, inplace=True)

            # df = pd.concat([df_train, df_test])
            # df = df.sort_values(['unique_id', 'ds']).reset_index(drop=True)

            S_df = S_df.sort_values("unique_id").reset_index(drop=True)

        X_df = None
        if cache:
            pd.to_pickle((df_train, df_test, X_df, S_df), file_cache)

        return df_train, df_test, None, S_df

    @staticmethod
    def download(directory: str, group: str) -> None:
        """Download M4 Dataset."""
        path = f"{directory}/m4/datasets/"
        if not os.path.exists(path):
            # for group in M4Info.groups:
            download_file(path, f"{M4.source_url}/Train/{group}-train.csv")
            download_file(path, f"{M4.source_url}/Test/{group}-test.csv")
            download_file(path, f"{M4.source_url}/M4-info.csv")
            download_file(path, M4.naive2_forecast_url, decompress=True)


# Cell
class M4Evaluation:
    @staticmethod
    def load_benchmark(
        directory: str, group: str, source_url: Optional[str] = None
    ) -> np.ndarray:
        """Downloads and loads a bechmark forecasts.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        group: str
            Group name.
            Allowed groups: 'Yearly', 'Quarterly', 'Monthly',
                            'Weekly', 'Daily', 'Hourly'.
        source_url: str, optional
            Optional benchmark url obtained from
            https://github.com/Nixtla/m4-forecasts/tree/master/forecasts.
            If `None` returns Naive2.

        Returns
        -------
        benchmark: numpy array
            Numpy array of shape (n_series, horizon).
        """
        path = f"{directory}/m4/datasets"
        initial = group[0]
        if source_url is not None:
            filename = source_url.split("/")[-1].replace(".zip", ".csv")
            filepath = f"{path}/{filename}"
            if not os.path.exists(filepath):
                download_file(path, source_url, decompress=True)

        else:
            filepath = f"{path}/submission-Naive2.csv"

        benchmark = pd.read_csv(filepath)
        benchmark = benchmark[benchmark["id"].str.startswith(initial)]
        benchmark = benchmark.set_index("id").dropna(1)
        benchmark = benchmark.sort_values("id").values

        return benchmark

    @staticmethod
    def evaluate(
        directory: str, group: str, y_hat: Union[np.ndarray, str]
    ) -> pd.DataFrame:
        """Evaluates y_hat according to M4 methodology.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        group: str
            Group name.
            Allowed groups: 'Yearly', 'Quarterly', 'Monthly',
                            'Weekly', 'Daily', 'Hourly'.
        y_hat: numpy array, str
            Group forecasts as numpy array or
            benchmark url from
            https://github.com/Nixtla/m4-forecasts/tree/master/forecasts.

        Returns
        -------
        evaluation: pandas dataframe
            DataFrame with columns OWA, SMAPE, MASE
            and group as index.
        """
        if y_hat is None or isinstance(y_hat, str):
            y_hat = M4Evaluation.load_benchmark(directory, group, y_hat)

        group[0]
        class_group = M4Info[group]
        horizon = class_group.horizon
        seasonality = class_group.seasonality

        y_hat = y_hat["y"].values.reshape(-1, horizon)

        df_train, df_test, _, S_df = M4.load(directory="data", group=group)

        y_train = df_train.groupby("unique_id")["y"]
        y_train = y_train.apply(lambda x: x.values)
        y_train = y_train.values

        y_test = df_test["y"].values.reshape(-1, horizon)

        naive2 = M4Evaluation.load_benchmark(directory, group)
        smape_y_hat = smape(y_test, y_hat)
        smape_naive2 = smape(y_test, naive2)

        mases_y_hat = [
            mase(y_test[i], y_hat[i], y_train[i], seasonality)
            for i in range(class_group.n_ts)
        ]

        mase_y_hat = np.mean(mases_y_hat)
        mase_naive2 = np.mean(
            [
                mase(y_test[i], naive2[i], y_train[i], seasonality)
                for i in range(class_group.n_ts)
            ]
        )

        owa = 0.5 * (mase_y_hat / mase_naive2 + smape_y_hat / smape_naive2)

        evaluation = pd.DataFrame(
            {"SMAPE": smape_y_hat, "MASE": mase_y_hat, "OWA": owa}, index=[group]
        )

        smape_ts = smape(y_test, y_hat, axis=0)

        return evaluation, mases_y_hat, smape_ts


def evaluate_M4(dataset, forecasts, root_dir):
    METRICS = {"sMAPE", "MASE"}
    LOSSES_DICT = {
        "M4-Daily": {
            "sMAPE": {
                "ESRNN": 3.170,
                "FFORMA": 3.097,
                "Theta": 3.053,
                "ARIMA": 3.193,
                "ETS": 3.046,
                "Naive1": 3.045,
                "Naive2": 3.045,
                "RNN": 5.964,
                "MLP": 9.321,
            },
            "MASE": {
                "ESRNN": 3.446,
                "FFORMA": 3.344,
                "Theta": 3.262,
                "ARIMA": 3.410,
                "ETS": 3.253,
                "Naive1": 3.278,
                "Naive2": 3.278,
                "RNN": 6.232,
                "MLP": 12.973,
            },
        },
        "M4-Yearly": {
            "sMAPE": {
                "NBEATS": 13.114,
                "ESRNN": 13.176,
                "FFORMA": 13.528,
                "Theta": 14.593,
                "ARIMA": 15.168,
                "ETS": 15.356,
                "Naive1": 16.342,
                "Naive2": 16.342,
                "RNN": 22.398,
                "MLP": 21.764,
            },
            "MASE": {
                "ESRNN": 2.980,
                "FFORMA": 3.060,
                "Theta": 3.382,
                "ARIMA": 3.402,
                "ETS": 3.444,
                "Naive1": 3.974,
                "Naive2": 3.974,
                "RNN": 4.946,
                "MLP": 4.946,
            },
        },
        "M4-Quarterly": {
            "sMAPE": {
                "NBEATS": 9.154,
                "ESRNN": 9.679,
                "FFORMA": 9.733,
                "Theta": 10.311,
                "ARIMA": 10.431,
                "ETS": 10.291,
                "Naive1": 11.610,
                "Naive2": 11.012,
                "RNN": 17.027,
                "MLP": 18.500,
            },
            "MASE": {
                "ESRNN": 1.118,
                "FFORMA": 1.111,
                "Theta": 1.232,
                "ARIMA": 1.165,
                "ETS": 1.161,
                "Naive1": 1.477,
                "Naive2": 1.371,
                "RNN": 2.016,
                "MLP": 2.314,
            },
        },
        "M4-Monthly": {
            "sMAPE": {
                "NBEATS": 12.041,
                "ESRNN": 12.126,
                "FFORMA": 12.639,
                "Theta": 13.002,
                "ARIMA": 13.443,
                "ETS": 13.525,
                "Naive1": 15.256,
                "Naive2": 14.427,
                "RNN": 24.056,
                "MLP": 24.333,
            },
            "MASE": {
                "ESRNN": 0.884,
                "FFORMA": 0.893,
                "Theta": 0.970,
                "ARIMA": 0.930,
                "ETS": 0.948,
                "Naive1": 1.205,
                "Naive2": 1.063,
                "RNN": 1.601,
                "MLP": 1.925,
            },
        },
        "M4-Weekly": {
            "sMAPE": {
                "ESRNN": 7.817,
                "FFORMA": 7.625,
                "Theta": 9.093,
                "ARIMA": 8.653,
                "ETS": 8.727,
                "Naive1": 9.161,
                "Naive2": 9.161,
                "RNN": 15.220,
                "MLP": 21.349,
            },
            "MASE": {
                "ESRNN": 2.356,
                "FFORMA": 2.108,
                "Theta": 2.637,
                "ARIMA": 2.556,
                "ETS": 2.527,
                "Naive1": 2.777,
                "Naive2": 2.777,
                "RNN": 5.132,
                "MLP": 13.568,
            },
        },
        "M4-Hourly": {
            "sMAPE": {
                "ESRNN": 9.328,
                "FFORMA": 11.506,
                "Theta": 18.138,
                "ARIMA": 13.980,
                "ETS": 17.307,
                "Naive1": 43.003,
                "Naive2": 18.383,
                "RNN": 14.698,
                "MLP": 13.842,
            },
            "MASE": {
                "ESRNN": 0.893,
                "FFORMA": 0.819,
                "Theta": 2.455,
                "ARIMA": 0.943,
                "ETS": 1.824,
                "Naive1": 11.608,
                "Naive2": 2.395,
                "RNN": 3.048,
                "MLP": 2.607,
            },
        },
    }

    group = dataset.split("-")[1]
    losses_dict = LOSSES_DICT[dataset]
    logger.info("DATASET: M4 dataset, GROUP: ", group)
    evaluation, mases_y_hat, smape_ts = M4Evaluation.evaluate(
        y_hat=forecasts, directory="./data", group=group
    )
    model_losses = {"sMAPE": evaluation["SMAPE"][0], "MASE": evaluation["MASE"][0]}

    # Bar plot comparing models
    loss_benchmark(
        metrics=METRICS,
        model_losses=model_losses,
        losses_dict=losses_dict,
        root_dir=root_dir,
    )

    # Histogram of MASE by time serie
    loss_per_serie(losses=mases_y_hat, root_dir=root_dir)

    # SMAPE by horizon
    loss_per_timestamp(losses=smape_ts, root_dir=root_dir)
