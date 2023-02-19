"""Copied from https://github.com/Nixtla/nixtla/tree/main/tsbenchmarks/benchmarks

python m5.py \
--dataset M5 \
--filename train/M5-forecasts-benchmark.csv \
--unique-id-column unique_id \
--ds-column ds \
--y-column y
"""
import logging
import os
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd

from dagster_playground.assets.ml.utils import (
    download_file,
    loss_benchmark,
)

logger = logging.getLogger(__name__)


# Cell
@dataclass
class M5:
    # original data available from Kaggle directly
    # pip install kaggle --upgrade
    # kaggle competitions download -c m5-forecasting-accuracy
    source_url: str = "https://github.com/Nixtla/m5-forecasts/raw/main/datasets/m5.zip"

    @staticmethod
    def download(directory: str) -> None:
        """Downloads M5 Competition Dataset."""
        path = f"{directory}/m5/datasets"
        if not os.path.exists(path):
            download_file(directory=path, source_url=M5.source_url, decompress=True)

    @staticmethod
    def load(
        directory: str, cache: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Downloads and loads M5 data.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        cache: bool
            If `True` saves and loads.

        Notes
        -----
        [1] Returns train+test sets.
        [2] Based on https://www.kaggle.com/lemuz90/m5-preprocess.
        """
        path = f"{directory}/m5/datasets"
        file_cache = f"{path}/m5.p"

        if os.path.exists(file_cache) and cache:
            Y_df, X_df, S_df = pd.read_pickle(file_cache)

            return Y_df, X_df, S_df

        M5.download(directory)
        # Calendar data
        cal_dtypes = {
            "wm_yr_wk": np.uint16,
            "event_name_1": "category",
            "event_type_1": "category",
            "event_name_2": "category",
            "event_type_2": "category",
            "snap_CA": np.uint8,
            "snap_TX": np.uint8,
            "snap_WI": np.uint8,
        }
        cal = pd.read_csv(
            f"{path}/calendar.csv",
            dtype=cal_dtypes,
            usecols=[*list(cal_dtypes.keys()), "date"],
            parse_dates=["date"],
        )
        cal["d"] = np.arange(cal.shape[0]) + 1
        cal["d"] = "d_" + cal["d"].astype("str")
        cal["d"] = cal["d"].astype("category")

        event_cols = [k for k in cal_dtypes if k.startswith("event")]
        for col in event_cols:
            cal[col] = cal[col].cat.add_categories("nan").fillna("nan")

        # Prices
        prices_dtypes = {
            "store_id": "category",
            "item_id": "category",
            "wm_yr_wk": np.uint16,
            "sell_price": np.float32,
        }

        prices = pd.read_csv(f"{path}/sell_prices.csv", dtype=prices_dtypes)

        # Sales
        sales_dtypes = {
            "item_id": prices.item_id.dtype,
            "dept_id": "category",
            "cat_id": "category",
            "store_id": "category",
            "state_id": "category",
            **{f"d_{i+1}": np.float32 for i in range(1969)},
        }
        # Reading train and test sets
        sales_train = pd.read_csv(
            f"{path}/sales_train_evaluation.csv", dtype=sales_dtypes
        )
        sales_test = pd.read_csv(
            f"{path}/sales_test_evaluation.csv", dtype=sales_dtypes
        )
        sales = sales_train.merge(
            sales_test,
            how="left",
            on=["item_id", "dept_id", "cat_id", "store_id", "state_id"],
        )
        sales["id"] = (
            sales[["item_id", "store_id"]]
            .astype(str)
            .agg("_".join, axis=1)
            .astype("category")
        )
        # Long format
        long = sales.melt(
            id_vars=["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"],
            var_name="d",
            value_name="y",
        )
        long["d"] = long["d"].astype(cal.d.dtype)
        long = long.merge(cal, on=["d"])
        long = long.merge(prices, on=["store_id", "item_id", "wm_yr_wk"])
        long = long.drop(columns=["d", "wm_yr_wk"])

        def first_nz_mask(values, index):
            """Return a boolean mask where the True starts at the first non-zero value."""
            mask = np.full(values.size, True)
            for idx, value in enumerate(values):
                if value == 0:
                    mask[idx] = False
                else:
                    break
            return mask

        long = long.sort_values(["id", "date"], ignore_index=True)
        keep_mask = long.groupby("id")["y"].transform(first_nz_mask, engine="numba")
        long = long[keep_mask.astype(bool)]
        long.rename(columns={"id": "unique_id", "date": "ds"}, inplace=True)
        Y_df = long.filter(items=["unique_id", "ds", "y"])
        cats = ["item_id", "dept_id", "cat_id", "store_id", "state_id"]
        S_df = long.filter(items=["unique_id", *cats])
        S_df = S_df.drop_duplicates(ignore_index=True)
        X_df = long.drop(columns=["y", *cats])

        if cache:
            pd.to_pickle((Y_df, X_df, S_df), file_cache)

        return Y_df, X_df, S_df


# Cell
class M5Evaluation:
    levels: dict = {
        "Level1": ["total"],
        "Level2": ["state_id"],
        "Level3": ["store_id"],
        "Level4": ["cat_id"],
        "Level5": ["dept_id"],
        "Level6": ["state_id", "cat_id"],
        "Level7": ["state_id", "dept_id"],
        "Level8": ["store_id", "cat_id"],
        "Level9": ["store_id", "dept_id"],
        "Level10": ["item_id"],
        "Level11": ["state_id", "item_id"],
        "Level12": ["item_id", "store_id"],
    }

    @staticmethod
    def aggregate_levels(
        y_hat: pd.DataFrame, categories: pd.DataFrame = None
    ) -> pd.DataFrame:
        """Aggregates the 30_480 series to get 42_840."""
        y_hat_cat = y_hat.assign(total="Total")

        df_agg = []
        for level, agg in M5Evaluation.levels.items():
            df = y_hat_cat.groupby(agg).sum().reset_index()
            renamer = dict(zip(agg, ["Agg_Level_1", "Agg_Level_2"]))
            df.rename(columns=renamer, inplace=True)
            df.insert(0, "Level_id", level)
            df_agg.append(df)
        df_agg = pd.concat(df_agg)
        df_agg = df_agg.fillna("X")
        df_agg = df_agg.set_index(["Level_id", "Agg_Level_1", "Agg_Level_2"])
        df_agg.columns = [f"d_{i+1}" for i in range(df_agg.shape[1])]

        return df_agg

    @staticmethod
    def evaluate(directory: str, y_hat: pd.DataFrame) -> pd.DataFrame:
        """Evaluates y_hat according to M4 methodology.

        Parameters
        ----------
        directory: str
            Directory where data will be downloaded.
        y_hat: pandas datafrae, str
            Forecasts as wide pandas dataframe with columns
            ['unique_id'] and forecasts or
            benchmark url from
            https://github.com/Nixtla/m5-forecasts/tree/main/forecasts.

        Returns
        -------
        evaluation: pandas dataframe
            DataFrame with columns OWA, SMAPE, MASE
            and group as index.
        """
        logger.info("Downlading M5 data")
        M5.download(directory)

        # Merge with s_df
        y_hat = y_hat.set_index(["unique_id", "ds"]).unstack()
        y_hat = y_hat.droplevel(0, 1).reset_index()
        *_, s_df = M5.load(directory)
        y_hat = y_hat.merge(s_df, how="left", on=["unique_id"])

        path = f"{directory}/m5/datasets"

        weights = pd.read_csv(f"{path}/weights_evaluation.csv")
        sales = pd.read_csv(f"{path}/sales_train_evaluation.csv")
        y_test = pd.read_csv(f"{path}/sales_test_evaluation.csv")

        # sales
        sales = M5Evaluation.aggregate_levels(sales)

        def scale(x):
            x = x.values
            x = x[np.argmax(x != 0) :]
            scale = ((x[1:] - x[:-1]) ** 2).mean()
            return scale

        scales = sales.agg(scale, 1).rename("scale").reset_index()

        # y_test
        y_test = M5Evaluation.aggregate_levels(y_test)

        # y_hat
        y_hat = M5Evaluation.aggregate_levels(y_hat)

        score = (y_test - y_hat) ** 2
        score = score.mean(1)
        score = score.rename("rmse").reset_index()
        score = score.merge(
            weights, how="left", on=["Level_id", "Agg_Level_1", "Agg_Level_2"]
        )
        score = score.merge(
            scales, how="left", on=["Level_id", "Agg_Level_1", "Agg_Level_2"]
        )
        score["wrmsse"] = (score["rmse"] / score["scale"]).pow(1 / 2) * score["weight"]
        score = score.groupby("Level_id")[["wrmsse"]].sum()
        score = score.loc[M5Evaluation.levels.keys()]
        total = score.mean().rename("Total").to_frame().T
        score = pd.concat([total, score])

        return score


def evaluate_M5(forecasts, root_dir):
    METRICS = {"WRMSSE"}
    LOSSES_DICT = {
        "WRMSSE": {
            "Naive": 1.752,
            "sNaive": 0.847,
            "MLP": 0.977,
            "RF": 1.010,
            "YJ_STU_1st": 0.520,
            "Matthias_2nd": 0.528,
            "mf_3rd": 0.536,
            "Rp_50th": 0.576,
            "AmazonF": 0.789085,
            "FBProphet": 0.720,
        }
    }

    wrmsse = M5Evaluation.evaluate(y_hat=forecasts, directory="./data")

    model_losses = {"WRMSSE": wrmsse["wrmsse"].values[0]}

    # Bar plot comparing models
    loss_benchmark(
        metrics=METRICS,
        model_losses=model_losses,
        losses_dict=LOSSES_DICT,
        root_dir=root_dir,
    )

    LOSSES_DICT["WRMSSE"]["YourModel"] = model_losses["WRMSSE"]

    losses_df = pd.DataFrame.from_dict(LOSSES_DICT).rename_axis("model").reset_index()
    losses_df.sort_values(by="WRMSSE", inplace=True)
    losses_df["WRMSSE"] = losses_df["WRMSSE"].round(3)

    return losses_df
