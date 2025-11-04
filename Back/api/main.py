# main.py (API backend) — MySQL ready
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import traceback

from Back.Data.animeDAO import AnimeDAO
from Back.Data.userDAO import UserDAO
from Back.Trainer.trainer import train_model
from Back.Recommendator.recommender import (
    get_user_watched,
    get_similar_anime,
    get_user_recommendations,
)

app = FastAPI(title="Anime Recommendation API")
anime_dao = AnimeDAO()
user_dao = UserDAO()


class RecommendationRequest(BaseModel):
    anime_id: Optional[int] = None
    user_id: Optional[int] = None
    min_ratings: int = 100
    top_n: int = 10
    genre_weight: float = 0.2
    rating_weight: float = 0.1


@app.get("/")
def root():
    return {"message": "Anime Recommendation API running"}

# Models
class AuthRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/register")
def register_user(req: AuthRequest):
    try:
        result = user_dao.create_user(req.username, req.password)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login")
def login_user(req: AuthRequest):
    try:
        result = user_dao.authenticate_user(req.username, req.password)
        if result["status"] == "error":
            raise HTTPException(status_code=401, detail=result["message"])
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anime/search")
def search_anime(query: str = Query(..., description="Anime name or ID to search")):
    """Search anime by name or ID from the database."""
    try:
        anime_df = anime_dao.load_anime()

        if query.isdigit():
            result = anime_df[anime_df["anime_id"] == int(query)]
        else:
            result = anime_df[anime_df["name"].str.lower().str.contains(query.lower(), na=False)]

        if result.empty:
            raise HTTPException(status_code=404, detail="No anime found for this query")

        return result.to_dict(orient="records")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
def train():
    try:
        meta = train_model()
        version = anime_dao.get_current_model_version()
        return {"status": "success", "version": version, "meta": meta}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-version")
def get_model_version():
    try:
        version = anime_dao.get_current_model_version()
        return {"current_model_version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/watched")
def get_watched(user_id: int):
    try:
        watched = get_user_watched(user_id)
        if watched.empty:
            raise HTTPException(status_code=404, detail="User not found or no watched anime")
        return watched.to_dict(orient="records")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommend/user/{user_id}")
def recommend_for_user(user_id: int):
    try:
        recs = get_user_recommendations(user_id)
        if recs is None or recs.empty:
            return {"status": "error", "message": "No recommendations found"}
        return {"status": "success", "user_id": user_id, "recommendations": recs.to_dict(orient="records")}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommend/anime/{anime_id}")
def recommend_for_anime(anime_id: int, top_n: int = 10):
    try:
        recs = get_similar_anime(anime_id, top_n=top_n)
        if recs is None or recs.empty:
            return {"status": "error", "message": "No similar anime found"}
        return {"status": "success", "anime_id": anime_id, "recommendations": recs.to_dict(orient="records")}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
