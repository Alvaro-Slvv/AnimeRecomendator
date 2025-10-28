# AnimeRecomendator
## Project Description
This is a small-scale project built using a 
[Kaggle dataset](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database) for data science practice, focusing on data structures, cleaning, and exploratory analysis.

The main objective is to experiment with different data-oriented machine learning approaches and implement an API-based architecture that cleanly separates the backend (model training and recommendation logic) from the frontend (console interface).
## Features
- Automated model training and versioning  
- User-based and anime-based recommendations  
- Genre and rating weight tuning  
- DAO layer separating data access from core logic  
- REST API endpoints for all key operations

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Install dependencies

Run this in the project root:
```bash
pip install -r requirements.txt
```
## Endpoints
| Method | Endpoint | Description |
| :---: | :--- | :--- |
| GET | / | Health check | 
| POST |	/train |	Train and version a new model |
| GET |	/model-version |	Get current model version |
| GET | /user/{user_id}/watched |	Get anime a user has watched and rated |
| GET |	/recommend/user/{user_id} |	Recommend new anime for a user |
| GET |	/recommend/anime/{anime_id} |	Get similar anime to a given anime |

## Running the application
### Step 1 — Start the API Server

Open a terminal in the project root and run:
```bash
python run_api.py
```

This will start the FastAPI backend at:

🔗 http://127.0.0.1:8000

Expected output:
```json
{"message": "Anime Recommendation API is running!"}
```

### Step 2 — Launch the Console Interface

In another terminal (with the API running), execute:

```bash
python Front/consola.py
```

You’ll see the console menu:
```bash
=== Consola de AnimeRecomendator ===
1. Obtener recomendaciones
2. Entrenar el algoritmo
3. Obtener la versión del modelo
4. Salir
```
