import logging
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cell
def divide_no_nan(a, b):
    """
    Auxiliary funtion to handle divide by 0
    """
    div = a / b
    div[div != div] = 0.0
    div[div == float("inf")] = 0.0
    return div


# Cell
def metric_protections(y: np.ndarray, y_hat: np.ndarray, weights: np.ndarray):
    assert (weights is None) or (np.sum(weights) > 0), "Sum of weights cannot be 0"
    assert (weights is None) or (weights.shape == y_hat.shape), "Wrong weight dimension"


# Cell
def smape(
    y: np.ndarray,
    y_hat: np.ndarray,
    weights: Optional[np.ndarray] = None,
    axis: Optional[int] = None,
) -> Union[float, np.ndarray]:
    """Calculates Symmetric Mean Absolute Percentage Error.

    SMAPE measures the relative prediction accuracy of a
    forecasting method by calculating the relative deviation
    of the prediction and the true value scaled by the sum of the
    absolute values for the prediction and true value at a
    given time, then averages these devations over the length
    of the series. This allows the SMAPE to have bounds between
    0% and 200% which is desireble compared to normal MAPE that
    may be undetermined.

    Parameters
    ----------
    y: numpy array
        Actual test values.
    y_hat: numpy array
        Predicted values.
    weights: numpy array
        Weights for weighted average.
    axis: None or int, optional
        Axis or axes along which to average a.
        The default, axis=None, will average over all of the
        elements of the input array.
        If axis is negative it counts
        from the last to the first axis.

    Returns
    -------
    smape: numpy array or double
        Return the smape along the specified axis.
    """
    MAX_SMAPE = 200

    metric_protections(y, y_hat, weights)

    delta_y = np.abs(y - y_hat)
    scale = np.abs(y) + np.abs(y_hat)
    smape = divide_no_nan(delta_y, scale)
    smape = 200 * np.average(smape, weights=weights, axis=axis)

    if isinstance(smape, float):
        assert smape <= MAX_SMAPE, f"SMAPE should be lower than {MAX_SMAPE}"
    else:
        assert all(smape <= MAX_SMAPE), f"SMAPE should be lower than {MAX_SMAPE}"

    return smape


# Cell
def mase(  # noqa: PLR0913
    y: np.ndarray,
    y_hat: np.ndarray,
    y_train: np.ndarray,
    seasonality: int,
    weights: Optional[np.ndarray] = None,
    axis: Optional[int] = None,
) -> Union[float, np.ndarray]:
    """Calculates the Mean Absolute Scaled Error.

    MASE measures the relative prediction accuracy of a
    forecasting method by comparinng the mean absolute errors
    of the prediction and the true value against the mean
    absolute errors of the seasonal naive model.

    Parameters
    ----------
    y: numpy array
        Actual test values.
    y_hat: numpy array
        Predicted values.
    y_train: numpy array
        Actual insample values for Seasonal Naive predictions.
    seasonality: int
        Main frequency of the time series
        Hourly 24,  Daily 7, Weekly 52,
        Monthly 12, Quarterly 4, Yearly 1.
    weights: numpy array
        Weights for weighted average.
    axis: None or int, optional
        Axis or axes along which to average a.
        The default, axis=None, will average over all of the
        elements of the input array.
        If axis is negative it counts
        from the last to the first axis.

    Returns
    -------
    mase: numpy array or double
        Return the mase along the specified axis.

    References
    ----------
    [1] https://robjhyndman.com/papers/mase.pdf
    """
    delta_y = np.abs(y - y_hat)
    delta_y = np.average(delta_y, weights=weights, axis=axis)

    scale = np.abs(y_train[:-seasonality] - y_train[seasonality:])
    scale = np.average(scale, axis=axis)

    mase = delta_y / scale

    return mase


# Cell
def download_file(directory: str, source_url: str, decompress: bool = False) -> None:
    """Download data from source_ulr inside directory.

    Parameters
    ----------
    directory: str, Path
        Custom directory where data will be downloaded.
    source_url: str
        URL where data is hosted.
    decompress: bool
        Wheter decompress downloaded file. Default False.
    """
    if isinstance(directory, str):
        directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    filename = source_url.split("/")[-1]
    filepath = Path(f"{directory}/{filename}")

    # Streaming, so we can iterate over the response.
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(source_url, stream=True, headers=headers)
    # Total size in bytes.
    total_size = int(r.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    t = tqdm(total=total_size, unit="iB", unit_scale=True)
    with open(filepath, "wb") as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
            f.flush()
    t.close()

    if total_size != 0 and t.n != total_size:
        logger.error("ERROR, something went wrong downloading data")

    size = filepath.stat().st_size
    logger.info(f"Successfully downloaded {filename}, {size}, bytes.")

    if decompress:
        if ".zip" in filepath.suffix:
            logger.info("Decompressing zip file...")
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(directory)
        else:
            from patoolib import extract_archive

            extract_archive(filepath, outdir=directory)
        logger.info(f"Successfully decompressed {filepath}")


def loss_benchmark(metrics, model_losses, losses_dict, root_dir):
    for metric in metrics:
        loss_dict = losses_dict[metric]
        loss_dict["YourModel"] = model_losses[metric]
        final_dict = dict(sorted(loss_dict.items(), key=lambda item: item[1]))

        colors = len(final_dict) * ["#6e8e9e"]
        colors[list(final_dict.keys()).index("YourModel")] = "#e1ad9b"

        plt.figure(figsize=(10, 5))
        plt.bar(final_dict.keys(), final_dict.values(), color=colors)
        plt.xlabel("Model")
        plt.ylabel(metric)
        plt.grid()
        plt.savefig(root_dir + f"{metric}.pdf")


def loss_per_serie(losses, root_dir):
    plt.figure(figsize=(15, 7))
    plt.hist(losses, bins=50, color="#6e8e9e")
    plt.grid()
    plt.ylabel("Number of series")
    plt.xlabel("LOSS")
    plt.savefig(root_dir + "loss_per_serie.pdf")


def loss_per_timestamp(losses, root_dir):
    plt.figure(figsize=(15, 7))
    plt.plot(losses)
    plt.xlabel("H")
    plt.ylabel("SMAPE")
    plt.grid()
    plt.savefig(root_dir + "smape_per_timestamp.pdf")


def extract_file_from_zip(zip_file_bytes, filename):
    with ZipFile(BytesIO(zip_file_bytes)) as archive:
        full_path = [
            candidate_path
            for candidate_path in archive.namelist()
            if candidate_path.endswith(filename)
        ][0]
        return pd.read_csv(archive.open(full_path))


class RecommenderModel:
    def __init__(self, features, ids):
        self.features = features
        self.nn = NearestNeighbors(metric="cosine", n_jobs=-1)
        self.nn.fit(self.features)
        self.ids = ids

    def find_similar(self, id, n=5):
        index = self.ids.index(id)
        (top_indexes,) = self.nn.kneighbors(self.features[[index]], n, False)
        return [self.ids[index] for index in top_indexes]
