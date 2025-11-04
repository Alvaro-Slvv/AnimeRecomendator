import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class AnimeDAO:
    """Data Access Object for the anime recommendation system (MySQL + SQLAlchemy)."""

    def __init__(self):
        host = os.getenv("DB_HOST", "localhost")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "anime_recommender")
        port = os.getenv("DB_PORT", "3306")

        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    # ---------- Data Loading ----------

    def load_anime(self):
        query = text("SELECT * FROM animes;")
        anime = pd.read_sql(query, self.engine)
        anime.columns = anime.columns.str.strip().str.lower()
        if "anime_id" not in anime.columns and "id" in anime.columns:
            anime.rename(columns={"id": "anime_id"}, inplace=True)
        return anime

    def load_ratings(self):
        query = text("SELECT * FROM ratings;")
        ratings = pd.read_sql(query, self.engine)
        ratings.columns = ratings.columns.str.strip().str.lower()
        if "user_id" not in ratings.columns and "user" in ratings.columns:
            ratings.rename(columns={"user": "user_id"}, inplace=True)
        return ratings

    # ---------- Model Version Tracking ----------

    def save_model_version(self, version: str):
        with self.engine.begin() as conn:
            conn.execute(
                text("INSERT INTO model_versions (version, created_at) VALUES (:v, :t)"),
                {"v": version, "t": datetime.now()},
            )

    def get_current_model_version(self):
        query = text("SELECT version FROM model_versions ORDER BY created_at DESC LIMIT 1;")
        result = pd.read_sql(query, self.engine)
        if result.empty:
            return "none"
        return result.iloc[0]["version"]

    # ---------- Model Training Helper ----------

    def train_model(self):
        from Back.Trainer.trainer import train_model
        meta = train_model()
        version = self.get_current_model_version()
        return meta, version

    # ---------- Connection Management ----------

    def close(self):
        self.engine.dispose()
