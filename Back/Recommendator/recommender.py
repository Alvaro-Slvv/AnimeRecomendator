# Back/Recommendator/recommender.py

import pickle
import pandas as pd
from pathlib import Path
from Back.Trainer.trainer import get_current_model_version

DATA_DIR = Path("Back/Data")
MODELS_DIR = DATA_DIR / "models"

# --- Load base data ---
anime = pd.read_csv(DATA_DIR / "anime.csv")
ratings = pd.read_csv(DATA_DIR / "rating.csv")

anime.columns = anime.columns.str.strip().str.lower()
ratings.columns = ratings.columns.str.strip().str.lower()


def load_current_model():
    version = get_current_model_version()
    model_path = MODELS_DIR / f"anime_corr_{version}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model {model_path} not found. Train first.")
    return pd.read_pickle(model_path)


def get_user_watched(user_id: int):
    """Return anime watched and rated by a user."""
    watched = ratings[ratings["user_id"] == user_id]
    return watched.merge(anime[["anime_id", "name"]], on="anime_id", how="left")


def get_similar_anime(anime_id, min_ratings=100, top_n=20, genre_weight=0.2, rating_weight=0.1):
    corr_matrix = load_current_model()

    if anime_id not in corr_matrix.columns:
        return None

    similar = corr_matrix[anime_id].dropna().sort_values(ascending=False)

    stats = ratings.groupby("anime_id").agg({"rating": ["size", "mean"]})
    stats.columns = ["num_ratings", "avg_rating"]

    result = pd.DataFrame({"anime_id": similar.index, "similarity": similar.values})
    result = result.merge(stats, on="anime_id", how="left")

    filtered = result[result["num_ratings"] >= min_ratings]
    if filtered.empty:
        filtered = result[result["num_ratings"] >= 10]

    filtered = filtered.merge(anime[["anime_id", "name", "genre", "rating"]], on="anime_id", how="left")

    # --- Genre Similarity ---
    def genre_similarity(g1, g2):
        if pd.isna(g1) or pd.isna(g2):
            return 0
        s1, s2 = set(g1.split(", ")), set(g2.split(", "))
        return len(s1 & s2) / len(s1 | s2) if len(s1 | s2) > 0 else 0

    base_genre = anime.loc[anime["anime_id"] == anime_id, "genre"].values[0]
    base_rating = anime.loc[anime["anime_id"] == anime_id, "rating"].values[0]

    filtered["genre_sim"] = filtered["genre"].apply(lambda g: genre_similarity(base_genre, g))
    filtered["rating_diff"] = filtered["rating"].apply(lambda r: 1 - abs(r - base_rating) / 10 if pd.notna(r) else 0)

    filtered["final_score"] = (
        (1 - genre_weight - rating_weight) * filtered["similarity"]
        + genre_weight * filtered["genre_sim"]
        + rating_weight * filtered["rating_diff"]
    )

    return filtered.sort_values("final_score", ascending=False).head(top_n)


def get_user_recommendations(user_id, min_ratings=100, top_n=20, genre_weight=0.2, rating_weight=0.1):
    """Generate recommendations based on all anime a user has watched."""
    watched = get_user_watched(user_id)
    if watched.empty:
        return pd.DataFrame()

    watched_ids = watched["anime_id"].unique()
    all_recs = pd.DataFrame()

    for aid in watched_ids:
        recs = get_similar_anime(aid, min_ratings, top_n, genre_weight, rating_weight)
        if recs is not None:
            all_recs = pd.concat([all_recs, recs])

    # Remove watched anime and aggregate
    all_recs = all_recs[~all_recs["anime_id"].isin(watched_ids)]
    final = all_recs.groupby(["anime_id", "name"], as_index=False).agg({"final_score": "mean"})
    return final.sort_values("final_score", ascending=False).head(top_n)
