# AnimeRecomendator
## Project Description
This is a small-scale project built using a 
[Kaggle dataset](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database) for data science practice, focusing on data structures, cleaning, and exploratory analysis.

The main objective is to experiment with different data-oriented machine learning approaches and implement an API-based architecture that cleanly separates the backend (model training and recommendation logic) from the frontend (console interface).

## Features
- Automated model training and versioning  
- Anime-based recommendations  
- Genre and rating weight tuning  
- DAO layer separating data access from core logic  
- REST API endpoints for all key operations  
- Environment-based configuration using `.env`  
- Single-command launcher (`run_all.py`) for full stack startup  

## Requirements

- **Python 3.9 or higher**
- **MySQL 8.0 or higher**
- **pip** (Python package manager)

## Environment Setup

Create a `.env` file in the project root with the following content:

```env
# === Database configuration ===
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=animerecommendator

# === API configuration ===
API_HOST=127.0.0.1
API_PORT=8000
```

> 💡 The application will automatically create the database and required tables on first run.

## Endpoints
| Method | Endpoint | Description |
| :---: | :--- | :--- |
| GET | / | Health check | 
| POST | /train | Train and version a new model |
| GET | /model-version | Get current model version |
| GET | /user/{user_id}/watched | Get anime a user has watched and rated |
| GET | /recommend/user/{user_id} | Recommend new anime for a user |
| GET | /recommend/anime/{anime_id} | Get similar anime to a given anime |
| POST | /auth/register | Register a new user |
| POST | /auth/login | Log in an existing user |

## Running the application
### Step 1 — Launch the full system automatically

Simply run:

```bash
python run_all.py
```

This will:
- Install or update all dependencies automatically  
- Initialize the MySQL database and tables  
- Start the FastAPI backend  
- Wait for the API to be ready  
- Launch the console frontend (`Front/consola.py`)

### Step 2 — Interact with the Console Interface

You’ll see the console menu:
```bash
=== Consola de AnimeRecomendator ===
1. Obtener recomendaciones
2. Entrenar el algoritmo
3. Obtener la versión del modelo
4. Salir
```

### Step 3 — API Access

Once the API is running, you can also access the interactive documentation via:

🔗 **http://127.0.0.1:8000/docs**

This provides Swagger UI for testing endpoints such as `/train`, `/recommend`, or `/auth/register`.

---

## Notes
- The system uses **SQLAlchemy** and **pandas.read_sql()** for database access.  
- All credentials and configuration values are loaded from the `.env` file.  
- The `run_all.py` script is cross-platform (Windows, macOS, Linux).  
- When the console exits, the API shuts down automatically.

---

## Example Output
Example response for the health check endpoint:
```json
{"message": "Anime Recommendation API is running!"}
```
