import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def download_m4_dataset(m4id, save_path):
    """
    Downloads an M4 time series dataset given its ID and saves it to a CSV file.
    Returns a pandas DataFrame containing the dataset.
    """
    url = f"https://github.com/M4Competition/M4-methods/blob/master/Dataset/Train/{m4id}.csv?raw=true"
    data = pd.read_csv(url)
    # data = data.drop(columns=["V1"])
    # data.columns = ["ds", "y"]
    # data["ds"] = pd.to_datetime(data["ds"])
    data.to_csv(save_path, index=False)

    return data


def train_lightgbm_model(data_path):
    """
    Loads a time series dataset from a CSV file and trains a LightGBM model on it using the scikit-learn interface.
    Returns the trained model.
    """
    data = pd.read_csv(data_path)
    X = data.drop(columns=["y"])
    y = data["y"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    lgb_train = lgb.Dataset(X_train, y_train)
    # lgb_test = lgb.Dataset(X_test, y_test, reference=lgb_train)

    params = {"objective": "regression", "metric": "rmse"}

    model = lgb.LGBMRegressor(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=10,
        verbose=False,
    )

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    print(f"RMSE: {rmse:.3f}")

    return model


data = download_m4_dataset("Hourly-train", "hourly_train.csv")
# model = train_lightgbm_model("hourly_train.csv")
