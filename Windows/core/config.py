import os
from pathlib import Path

# --- Chemins de Base ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"

# Création des dossiers s'ils n'existent pas
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuration SQLite ---
DB_PATH = DATA_DIR / "pokeminou.db"

# --- Configuration Eufy ---
EUFY_WS_URL = "ws://localhost:3000"
# Remplace avec l'IP de ta caméra et tes identifiants (NAS/RTSP)
RTSP_URL = "rtsp://7fc03VEDquqTE8kY:w8ha3qJJM8CEw24I@10.0.0.217/live1"

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
