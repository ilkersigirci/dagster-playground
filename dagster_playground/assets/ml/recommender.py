from collections import Counter
from types import SimpleNamespace

import requests
from dagster import OpExecutionContext, asset
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction import FeatureHasher

from dagster_playground.assets.ml.utils import RecommenderModel, extract_file_from_zip


@asset(config_schema={"small": bool})
def movielens_zip(context: OpExecutionContext):
    small = context.op_config["small"]
    if small:
        url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    else:
        url = "https://files.grouplens.org/datasets/movielens/ml-latest.zip"

    return requests.get(url).content


@asset
def movielens_ratings(movielens_zip):
    return extract_file_from_zip(movielens_zip, "ratings.csv")


@asset
def movielens_movies(movielens_zip):
    return extract_file_from_zip(movielens_zip, "movies.csv")


@asset
def movie_to_users(movielens_ratings):
    # create a matrix: 1 row per movie, 1 column per user
    df = (
        movielens_ratings[["movieId", "userId"]]
        .groupby("movieId")
        .aggregate(set)
        .reset_index()
    )
    movie_ids = list(df["movieId"])
    fh = FeatureHasher()
    features = fh.fit_transform(
        [Counter(str(user_id) for user_id in user_ids) for user_ids in df["userId"]]
    )

    return SimpleNamespace(movie_ids=movie_ids, features=features)


@asset
def movie_to_features(movie_to_users):
    return SimpleNamespace(
        movie_ids=movie_to_users.movie_ids,
        features=TruncatedSVD(100, random_state=42).fit_transform(
            movie_to_users.features
        ),
    )


@asset
def movie_recommender_model(movie_to_features):
    return RecommenderModel(movie_to_features.features, movie_to_features.movie_ids)
