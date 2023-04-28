# ruff: noqa
import numpy as np
import pandas as pd
from dagster import Config, OpExecutionContext, asset, materialize
from sktime.forecasting.ets import AutoETS
from tqdm import tqdm

from dagster_playground.assets.ml.m4 import M4Info


class M4Config(Config):
    id: str = "Daily"


@asset
def original_m4_data(context: OpExecutionContext, config: M4Config) -> pd.DataFrame:
    """
    Downloads an M4 time series dataset given its ID.
    Returns a pandas DataFrame containing the dataset.
    """
    id = config.id
    uri = f"Train/{id}-train"
    # url = f"Test/{id}-test.csv"

    url = f"https://github.com/M4Competition/M4-methods/blob/master/Dataset/{uri}.csv?raw=true"
    # data = pd.read_csv(url, nrows=10)

    total_rows = M4Info[id].n_ts
    chunksize = 1000
    total = total_rows // chunksize + 1

    data = pd.concat(
        list(
            tqdm(
                pd.read_csv(url, chunksize=chunksize),
                desc="Loading data",
                total=total,
            )
        )
    )

    return data


@asset
def melt_m4_data(
    context: OpExecutionContext, original_m4_data: pd.DataFrame
) -> pd.Series:  # List[DynamicOutput[pd.Series]]:
    """
    Converts an M4 time series dataset from wide to long format.
    Returns a pandas DataFrame containing the dataset.
    """
    data = original_m4_data

    data.columns = ["unique_id", *list(range(1, data.shape[1]))]
    df = pd.melt(data, id_vars=["unique_id"], var_name="ds", value_name="y")
    df = df.dropna()

    df = df.groupby("unique_id")["y"]
    df = df.apply(lambda x: x.to_numpy())

    # FIXME: Find a way to add dataframe metadata to the dagster UI
    # context.add_output_metadata({"data_head": MetadataValue.json(df.head().to_dict())})

    return df

    # outputs = []
    # for idx in len(df):
    #     outputs.append(DynamicOutput(df.iloc[idx, :], mapping_key=idx))

    # return outputs


@asset(config_schema={"unique_id": str})
def one_m4_data(context: OpExecutionContext, melt_m4_data: pd.Series) -> pd.Series:
    """
    Returns one time series from an M4 dataset.
    """
    data = melt_m4_data[context.op_config["unique_id"]]

    serie = pd.Series(
        data,
        index=pd.period_range(
            start="2000-01-01", periods=len(data), freq="D", name="Period"
        ),
    )

    return serie


@asset
def train(one_m4_data: pd.Series) -> pd.Series:
    fh = np.arange(1, 8)
    sp = 1
    model = AutoETS(sp=sp)

    model.fit(one_m4_data)
    y_pred = model.predict(fh=fh)

    return y_pred


if __name__ == "__main__":
    asset_result = materialize(
        [original_m4_data],
        run_config={"ops": {"original_m4_data": {"config": {"m4id": "Daily"}}}},
    )

    result = asset_result.output_for_node("original_m4_data")

    print(result.head())
