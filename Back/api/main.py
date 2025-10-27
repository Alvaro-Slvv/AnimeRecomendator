from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import traceback

from Back.Data.dao import DataDAO
from Back.Trainer.trainer import train_model
from Back.Recommendator.recommender import (
    get_user_watched,
    get_similar_anime,
    get_user_recommendations,
)

app = FastAPI(title="Anime Recommendation API")
dao = DataDAO()

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

@app.post("/train")
def train():
    try:
        meta = train_model()
        version = dao.get_current_model_version()
        return {"status": "success", "version": version, "meta": meta}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-version")
def get_model_version():
    try:
        version = dao.get_current_model_version()
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
