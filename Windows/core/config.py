import os
from pathlib import Path
from dotenv import load_dotenv

# --- Chemins de Base ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"

# Charger le fichier .env à la racine
env_path = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Création des dossiers s'ils n'existent pas
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuration SQLite ---
DB_PATH = DATA_DIR / "pokeminou.db"

# --- Configuration Eufy ---
# La variable RTSP_URLS est définie dans le fichier .env à la racine (Y:\PokeMinou\.env)
_urls_raw = os.environ.get("RTSP_URLS", os.environ.get("RTSP_URL", ""))
RTSP_URLS = [url.strip() for url in _urls_raw.split(",")] if _urls_raw else []

# --- Configuration IA (YOLO) ---
YOLO_MODEL_PATH = BASE_DIR / "ai" / "weights" / "yolov8n.pt"
CAT_CLASS_ID = 15
CONFIDENCE_THRESHOLD = 0.5  # Modifiable via Gradio

# --- Configuration ReID (ResNet50) ---
COSINE_SIMILARITY_THRESHOLD = 0.8  # Seuil pour identifier le même chat

# --- Configuration Métier ---
COOLDOWN_MINUTES = 2  # Limite d'envoi de Push pour éviter le spam (modifiable via l'interface web)
IMAGE_RETENTION_DAYS_LOCAL = 30
IMAGE_RETENTION_HOURS_FIREBASE = 48

# --- Configuration Firebase ---
FIREBASE_CREDENTIALS_PATH = BASE_DIR / "serviceAccountKey.json"
FIREBASE_STORAGE_BUCKET = "pokeminou-b2530.firebasestorage.app"

# --- Persistance des Paramètres ---
import json

SETTINGS_FILE = DATA_DIR / "settings.json"

def load_settings():
    global CONFIDENCE_THRESHOLD, COOLDOWN_MINUTES
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                CONFIDENCE_THRESHOLD = data.get("CONFIDENCE_THRESHOLD", CONFIDENCE_THRESHOLD)
                COOLDOWN_MINUTES = data.get("COOLDOWN_MINUTES", COOLDOWN_MINUTES)
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")

def save_settings(conf, cooldown):
    global CONFIDENCE_THRESHOLD, COOLDOWN_MINUTES
    CONFIDENCE_THRESHOLD = conf
    COOLDOWN_MINUTES = cooldown
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({
                "CONFIDENCE_THRESHOLD": conf,
                "COOLDOWN_MINUTES": cooldown
            }, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des paramètres: {e}")

# Charger les paramètres persistants au démarrage
load_settings()
