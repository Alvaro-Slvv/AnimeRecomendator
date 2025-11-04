import pandas as pd
import os
import pickle
from datetime import datetime
from pathlib import Path
from Back.Data.animeDAO import AnimeDAO

dao = AnimeDAO()


def train_model():
    anime = dao.load_anime()
    ratings_raw = dao.load_ratings()

    ratings_raw = ratings_raw.rename(columns={
        "user_id": "user_id",
        "anime_id": "anime_id",
        "rating": "rating"
    })

    user_counts = ratings_raw["user_id"].value_counts()
    active_users = user_counts[user_counts >= 200].index
    ratings = ratings_raw[ratings_raw["user_id"].isin(active_users)]

    anime_counts = ratings["anime_id"].value_counts()
    popular_anime = anime_counts[anime_counts >= 50].index
    ratings = ratings[ratings["anime_id"].isin(popular_anime)]
    ratings = ratings[ratings["rating"] != -1]

    base_dir = Path("Back/Model")
    base_dir.mkdir(parents=True, exist_ok=True)

    version = datetime.now().strftime("v%Y%m%d_%H%M%S")
    corr_path = base_dir / f"anime_corr_matrix_{version}.pkl"
    meta_path = base_dir / f"anime_corr_meta_{version}.pkl"

    anime_pivot = ratings.pivot_table(index="user_id", columns="anime_id", values="rating")
    anime_corr_matrix = anime_pivot.corr(method="pearson", min_periods=10)

    with open(corr_path, "wb") as f:
        pickle.dump(anime_corr_matrix, f)

    meta = {"num_users": anime_pivot.shape[0], "num_anime": anime_pivot.shape[1]}
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)

    dao.save_model_version(version)
    return meta
