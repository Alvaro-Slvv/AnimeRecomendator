# Back/Trainer/utils.py
import pickle
from pathlib import Path

def save_pickle(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved object → {path}")

def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)
