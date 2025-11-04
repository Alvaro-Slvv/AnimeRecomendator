import os, sys, subprocess, time
from pathlib import Path

def ensure_core_dependencies():
    try:
        import dotenv, requests  # noqa: F401
    except ModuleNotFoundError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv", "requests"], check=True)

ensure_core_dependencies()

from dotenv import load_dotenv
import requests

def install_requirements():
    if not Path("requirements.txt").exists():
        print("requirements.txt not found."); return
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--pre", "numpy>=2.0.0"], check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)

def load_environment():
    if not Path(".env").exists():
        print(".env not found."); sys.exit(1)
    load_dotenv(".env")

def start_api():
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "Back.api.main:app", "--reload"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    return proc

def wait_for_api_ready(max_attempts=10):
    url = os.getenv("API_URL", "http://127.0.0.1:8000")
    for _ in range(max_attempts):
        try:
            if requests.get(url, timeout=2).status_code == 200: return True
        except requests.RequestException: pass
        time.sleep(2)
    return False

def start_frontend():
    subprocess.run([sys.executable, "Front/consola.py"], check=False)

def main():
    if sys.version_info < (3, 9):
        print("Python 3.9+ required."); sys.exit(1)
    install_requirements()
    load_environment()
    api_proc = start_api()
    if wait_for_api_ready():
        start_frontend()
    api_proc.terminate()
    print("All processes stopped.")

if __name__ == "__main__":
    main()
