# dao.py — SQLAlchemy refactor to remove pandas warnings
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime


class DataDAO:
    """
    Data Access Object for the anime recommendation system.
    Uses MySQL through SQLAlchemy (officially supported by pandas).
    """

    def __init__(self, host="localhost", user="root", password="123456", database="animerecommendator"):
        # SQLAlchemy connection string (using PyMySQL driver)
        db_url = f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4"
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    # ---------- Data Loading ----------

    def load_anime(self):
        """Load anime data as DataFrame."""
        query = text("SELECT * FROM animes;")
        anime = pd.read_sql(query, self.engine)
        anime.columns = anime.columns.str.strip().str.lower()
        if "anime_id" not in anime.columns and "id" in anime.columns:
            anime.rename(columns={"id": "anime_id"}, inplace=True)
        return anime

    def load_ratings(self):
        """Load user ratings as DataFrame."""
        query = text("SELECT * FROM ratings;")
        ratings = pd.read_sql(query, self.engine)
        ratings.columns = ratings.columns.str.strip().str.lower()
        if "user_id" not in ratings.columns and "user" in ratings.columns:
            ratings.rename(columns={"user": "user_id"}, inplace=True)
        return ratings

    # ---------- Model Version Tracking ----------

    def save_model_version(self, version: str):
        """Insert a new model version into model_versions."""
        with self.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO model_versions (version, created_at) VALUES (:v, :t)"),
                {"v": version, "t": datetime.now()},
            )

    def get_current_model_version(self):
        """Get latest model version."""
        query = text("SELECT version FROM model_versions ORDER BY created_at DESC LIMIT 1;")
        result = pd.read_sql(query, self.engine)
        if result.empty:
            return "none"
        return result.iloc[0]["version"]

    # ---------- Model Training Helper ----------

    def train_model(self):
        """Train model and return metadata + version."""
        from Back.Trainer.trainer import train_model
        meta = train_model()
        version = self.get_current_model_version()
        return meta, version

    # ---------- Connection Management ----------

    def close(self):
        self.engine.dispose()
