# AnimeRecomendator
## Project Description
This is a small-scale project built using a 
[Kaggle dataset](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database) for data science practice, focusing on data structures, cleaning, and exploratory analysis.

The main objective is to experiment with different data-oriented machine learning approaches and implement an API-based architecture that cleanly separates the backend (model training and recommendation logic) from the frontend (console interface).
## Features
- Automated model training and versioning  
- User-based and item-based recommendations  
- Genre and rating weight tuning  
- DAO layer for managing data and model persistence  
- REST API endpoints for all key operations
  
## Endpoints
| Method | Endpoint | Description |
| :---: | :--- | :--- |
| GET | / | Health check | 
| POST |	/train |	Train and version a new model |
| GET |	/model-version |	Get current model version |
| GET | /user/{user_id}/watched |	Get anime a user has watched and rated |
| GET |	/recommend/user/{user_id} |	Recommend new anime for a user |
| GET |	/recommend/anime/{anime_id} |	Get similar anime to a given anime |
