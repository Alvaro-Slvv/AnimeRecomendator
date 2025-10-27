import pandas as pd


def clean_data(anime: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """Apply filtering and cleaning rules to rating data."""
    user_counts = ratings["user_id"].value_counts()
    active_users = user_counts[user_counts >= 200].index
    ratings = ratings[ratings["user_id"].isin(active_users)]

    anime_counts = ratings["anime_id"].value_counts()
    popular_anime = anime_counts[anime_counts >= 50].index
    ratings = ratings[ratings["anime_id"].isin(popular_anime)]

    ratings = ratings[ratings["rating"] != -1]
    return ratings


def create_pivot_table(ratings: pd.DataFrame) -> pd.DataFrame:
    """Pivot user-anime ratings into a user-item matrix."""
    return ratings.pivot_table(index="user_id", columns="anime_id", values="rating")
