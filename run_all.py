import subprocess
import sys
import time
import requests
import os
import signal
import pymysql
from dotenv import load_dotenv

# === Python version check ===
if sys.version_info < (3, 9):
    print("Python 3.9 or higher is required to run this project.")
    sys.exit(1)

# === Load environment ===
if not os.path.exists(".env"):
    print("Missing .env file in project root.")
    sys.exit(1)

load_dotenv()

# === Config ===
MYSQL = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "anime_recommender")
}

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_URL = f"http://{API_HOST}:{API_PORT}/"
API_COMMAND = ["uvicorn", "Back.api.main:app", "--reload", "--port", str(API_PORT)]
FRONTEND_COMMAND = ["python", "Front/consola.py"]

# === Step 1: Install dependencies with auto-fallback ===
def install_requirements():
    """Install dependencies and handle fallback for new Python versions."""
    print("Checking dependencies (requirements.txt)...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("Dependencies installed.\n")

    except subprocess.CalledProcessError:
        print("Pip install failed — trying automatic recovery...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
        subprocess.run([sys.executable, "-m", "pip", "install", "--pre", "numpy>=2.0.0"])
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=False
        )
        print("Dependencies recovered successfully.\n")

# === Step 2: Ensure DB & Tables ===
def setup_database():
    print("Checking MySQL database...")
    try:
        conn = pymysql.connect(
            host=MYSQL["host"],
            user=MYSQL["user"],
            password=MYSQL["password"],
            port=MYSQL["port"],
            autocommit=True
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL['database']};")
        conn.select_db(MYSQL["database"])

        tables = {
            "animes": """
                CREATE TABLE IF NOT EXISTS animes (
                    anime_id INT PRIMARY KEY,
                    name VARCHAR(255),
                    genre TEXT,
                    type VARCHAR(50),
                    episodes INT,
                    rating FLOAT,
                    members INT
                );
            """,
            "ratings": """
                CREATE TABLE IF NOT EXISTS ratings (
                    user_id INT,
                    anime_id INT,
                    rating FLOAT,
                    PRIMARY KEY (user_id, anime_id)
                );
            """,
            "model_versions": """
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE,
                    password_hash VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """
        }

        for ddl in tables.values():
            cur.execute(ddl)

        print("Database and tables ready.\n")

    except Exception as e:
        print(f"MySQL setup failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

# === Step 3: API control ===
def api_is_running():
    try:
        r = requests.get(API_URL, timeout=2)
        if r.status_code == 200:
            print("🔄 API already running.")
            return True
    except requests.RequestException:
        pass
    return False

def start_api():
    print("Starting API server...")
    process = subprocess.Popen(API_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"API started with PID {process.pid}")
    return process

def wait_for_api_ready(timeout=30):
    print("Waiting for API to become ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(API_URL).status_code == 200:
                print("API is ready!\n")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    print("API did not start within timeout.")
    return False

# === Step 4: Launch Frontend ===
def run_frontend():
    print("Launching AnimeRecomendator CLI...\n")
    subprocess.run(FRONTEND_COMMAND)

# === Step 5: Main Orchestration ===
def main():
    api_process = None
    try:
        install_requirements()
        setup_database()

        api_running = api_is_running()
        if not api_running:
            api_process = start_api()
            if not wait_for_api_ready():
                print("Could not connect to API. Exiting.")
                if api_process:
                    api_process.terminate()
                sys.exit(1)
        else:
            print("Using existing API server.\n")

        run_frontend()

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if api_process:
            print("🔻 Stopping API server...")
            try:
                if os.name == "nt":
                    api_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    api_process.terminate()
                api_process.wait(timeout=5)
                print("API server stopped.")
            except Exception:
                pass

if __name__ == "__main__":
    main()
