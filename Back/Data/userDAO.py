# Back/Data/user_dao.py
from sqlalchemy import create_engine, text
from passlib.hash import bcrypt


class UserDAO:
    def __init__(self, host="localhost", user="root", password="", database="anime_recommender"):
        db_url = f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4"
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    def create_user(self, username: str, password: str):
        """Registers a new user if the username doesn't exist."""
        hashed_pw = bcrypt.hash(password)
        with self.engine.begin() as conn:
            existing = conn.execute(
                text("SELECT id FROM users WHERE username = :u"), {"u": username}
            ).fetchone()
            if existing:
                return {"status": "error", "message": "Username already exists"}

            conn.execute(
                text("INSERT INTO users (username, password) VALUES (:u, :p)"),
                {"u": username, "p": hashed_pw},
            )
        return {"status": "success", "message": "User registered successfully"}

    def authenticate_user(self, username: str, password: str):
        """Validates login credentials."""
        with self.engine.begin() as conn:
            result = conn.execute(
                text("SELECT id, password FROM users WHERE username = :u"),
                {"u": username},
            ).fetchone()

        if not result:
            return {"status": "error", "message": "User not found"}

        user_id, stored_hash = result
        if not bcrypt.verify(password, stored_hash):
            return {"status": "error", "message": "Invalid password"}

        return {"status": "success", "user_id": user_id}
