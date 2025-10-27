# Back/Trainer/preprocess.py
import pandas as pd
from pathlib import Path

def load_and_clean_data(base_dir: Path):
    anime_path = base_dir / "anime.csv"
    ratings_path = base_dir / "rating.csv"

    print("Loading raw data...")
    anime = pd.read_csv(anime_path)
    ratings_raw = pd.read_csv(ratings_path)

    anime = anime.rename(columns={'name': 'title'}) if 'name' in anime.columns else anime
    ratings_raw = ratings_raw.rename(columns={'user_id': 'user_id', 'anime_id': 'anime_id', 'rating': 'rating'})

    print(f"Raw data loaded: {len(anime)} anime, {len(ratings_raw)} ratings")

    user_counts = ratings_raw['user_id'].value_counts()
    active_users = user_counts[user_counts >= 200].index
    ratings = ratings_raw[ratings_raw['user_id'].isin(active_users)]

    anime_counts = ratings['anime_id'].value_counts()
    popular_anime = anime_counts[anime_counts >= 50].index
    ratings = ratings[ratings['anime_id'].isin(popular_anime)]

    rows_before = ratings_raw.shape[0]
    ratings = ratings[ratings['rating'] != -1]
    rows_after = ratings.shape[0]

    print(f"Cleaned ratings: {rows_after:,} from {rows_before:,} total")
    print(f"Removed {rows_before - rows_after:,} invalid or sparse entries")

    anime.columns = anime.columns.str.strip().str.lower()

    if 'id' in anime.columns and 'anime_id' not in anime.columns:
        anime.rename(columns={'id': 'anime_id'}, inplace=True)

    return anime, ratings
