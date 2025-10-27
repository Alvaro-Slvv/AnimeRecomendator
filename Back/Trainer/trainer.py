# Back/Trainer/trainer.py

import pickle
import json
from pathlib import Path
from datetime import datetime
from Back.Trainer.preprocess import load_and_clean_data

DATA_DIR = Path("Back/Data")
MODELS_DIR = DATA_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODEL_TRACK_FILE = DATA_DIR / "current_model.json"

def get_current_model_version() -> str:
    if MODEL_TRACK_FILE.exists():
        with open(MODEL_TRACK_FILE, "r") as f:
            data = json.load(f)
        return data.get("current_version", "v0")
    return "v0"

def train_model():
    anime, ratings = load_and_clean_data(DATA_DIR)

    print("📈 Building correlation matrix...")
    pivot = ratings.pivot_table(index="user_id", columns="anime_id", values="rating")
    corr_matrix = pivot.corr(method="pearson", min_periods=10)

    current_version = get_current_model_version()
    new_version_num = int(current_version.strip("v")) + 1 if current_version != "v0" else 1
    new_version = f"v{new_version_num}"

    corr_path = MODELS_DIR / f"anime_corr_{new_version}.pkl"
    meta_path = MODELS_DIR / f"anime_corr_meta_{new_version}.pkl"

    with open(corr_path, "wb") as f:
        pickle.dump(corr_matrix, f)

    meta = {"num_users": pivot.shape[0], "num_anime": pivot.shape[1], "trained_on": str(datetime.now())}
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)

    with open(MODEL_TRACK_FILE, "w") as f:
        json.dump({"current_version": new_version}, f, indent=4)

    print(f"✅ Model trained successfully — version {new_version}")
    return meta, new_version
