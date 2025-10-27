import pandas as pd
import json
from pathlib import Path


class DataDAO:
    def __init__(self, base_path: str = "Back/Data"):
        self.base_path = Path(base_path)
        self.anime_path = self.base_path / "anime.csv"
        self.ratings_path = self.base_path / "rating.csv"
        self.model_track_file = self.base_path / "current_model.json"

    def load_anime(self):
        anime = pd.read_csv(self.anime_path)
        anime.columns = anime.columns.str.strip().str.lower()
        if "anime_id" not in anime.columns:
            anime.rename(columns={"id": "anime_id"}, inplace=True)
        return anime

    def load_ratings(self):
        ratings = pd.read_csv(self.ratings_path)
        ratings.columns = ratings.columns.str.strip().str.lower()
        if "user_id" not in ratings.columns:
            ratings.rename(columns={"user": "user_id"}, inplace=True)
        return ratings

    def save_model_version(self, version: str):
        data = {"current_model_version": version}
        with open(self.model_track_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_current_model_version(self):
        if not self.model_track_file.exists():
            return "none"
        with open(self.model_track_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("current_model_version", "none")
