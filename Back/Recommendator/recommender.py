import pandas as pd
import pickle
from pathlib import Path
from Back.Data.dao import DataDAO

dao = DataDAO()
MODEL_DIR = Path("Back/Model")


def load_latest_model():
    version = dao.get_current_model_version()
    if version == "none":
        return None

    corr_path = MODEL_DIR / f"anime_corr_matrix_{version}.pkl"
    if not corr_path.exists():
        return None
    with open(corr_path, "rb") as f:
        return pickle.load(f)


def get_user_watched(user_id: int):
    ratings = dao.load_ratings()
    anime = dao.load_anime()
    user_data = ratings[ratings["user_id"] == user_id]
    return user_data.merge(anime, on="anime_id", how="left")


def get_similar_anime(anime_id, min_ratings=100, top_n=20, genre_weight=0.2, rating_weight=0.1):
    anime_corr_matrix = load_latest_model()
    if anime_corr_matrix is None or anime_id not in anime_corr_matrix.columns:
        return None

    anime = dao.load_anime()
    ratings = dao.load_ratings()

    similar = anime_corr_matrix[anime_id].dropna().sort_values(ascending=False)
    anime_stats = ratings.groupby("anime_id").agg({"rating": ["size", "mean"]})
    anime_stats.columns = ["num_ratings", "avg_rating"]

    result = pd.DataFrame({"anime_id": similar.index, "similarity": similar.values})
    result = result.merge(anime_stats, on="anime_id", how="left")
    filtered = result[result["num_ratings"] >= min_ratings]

    if filtered.empty:
        filtered = result[result["num_ratings"] >= 10]

    filtered = filtered.merge(anime[["anime_id", "name", "genre", "rating"]], on="anime_id", how="left")

    def genre_similarity(g1, g2):
        if pd.isna(g1) or pd.isna(g2):
            return 0
        s1, s2 = set(g1.split(", ")), set(g2.split(", "))
        return len(s1 & s2) / len(s1 | s2) if len(s1 | s2) > 0 else 0

    base_genre = anime.loc[anime["anime_id"] == anime_id, "genre"].values[0] if anime_id in anime["anime_id"].values else None
    filtered["genre_sim"] = filtered["genre"].apply(lambda g: genre_similarity(base_genre, g))

    base_rating = anime.loc[anime["anime_id"] == anime_id, "rating"].values[0] if anime_id in anime["anime_id"].values else None
    filtered["rating_diff"] = filtered["rating"].apply(
        lambda r: 1 - abs(r - base_rating) / 10 if pd.notna(r) and pd.notna(base_rating) else 0
    )

    filtered["final_score"] = (
        (1 - genre_weight - rating_weight) * filtered["similarity"]
        + genre_weight * filtered["genre_sim"]
        + rating_weight * filtered["rating_diff"]
    )

    return filtered.sort_values("final_score", ascending=False).head(top_n)


def get_user_recommendations(user_id: int, top_n: int = 10):
    user_watched = get_user_watched(user_id)
    if user_watched.empty:
        return None

    anime_ids = user_watched["anime_id"].tolist()
    all_recs = []

    for aid in anime_ids:
        recs = get_similar_anime(aid, top_n=top_n)
        if recs is not None:
            all_recs.append(recs)

    if not all_recs:
        return None

    combined = pd.concat(all_recs)
    combined = combined.groupby("anime_id").agg({"final_score": "mean"}).reset_index()
    combined = combined.merge(dao.load_anime()[["anime_id", "name", "genre", "rating"]], on="anime_id", how="left")
    combined = combined[~combined["anime_id"].isin(anime_ids)]

    return combined.sort_values("final_score", ascending=False).head(top_n)
