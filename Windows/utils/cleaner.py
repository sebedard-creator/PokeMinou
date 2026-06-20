import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from core.config import IMAGES_DIR, IMAGE_RETENTION_DAYS_LOCAL, IMAGE_RETENTION_HOURS_FIREBASE
from cloud.firebase_sync import firebase_mgr
from firebase_admin import storage

logger = logging.getLogger("Cleaner")

def cleanup_local_images():
    """Supprime les images locales vieilles de plus de X jours."""
    logger.info("Lancement du nettoyage local des images...")
    now = time.time()
    cutoff_time = now - (IMAGE_RETENTION_DAYS_LOCAL * 86400) # 86400 = 24h * 60m * 60s
    deleted_count = 0
    
    if IMAGES_DIR.exists():
        for file_path in IMAGES_DIR.glob("*.jpg"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Erreur suppression {file_path} : {e}")
                    
    logger.info(f"Nettoyage local terminé. {deleted_count} images supprimées.")

def cleanup_firebase_storage():
    """Supprime les images sur Firebase vieilles de plus de X heures."""
    if not firebase_mgr.is_initialized:
        return

    logger.info("Lancement du nettoyage Firebase Storage...")
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix="cats/")
        
        now = datetime.now(tz=None) # Timezone naive pour simplifier, ou à adapter avec pytz
        deleted_count = 0
        
        for blob in blobs:
            # blob.time_created est un objet datetime avec timezone (UTC)
            # On le convertit pour faire la soustraction
            blob_time = blob.time_created.replace(tzinfo=None) 
            age = now - blob_time
            
            if age > timedelta(hours=IMAGE_RETENTION_HOURS_FIREBASE):
                blob.delete()
                deleted_count += 1
                
        logger.info(f"Nettoyage Firebase terminé. {deleted_count} images supprimées.")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage Firebase : {e}")

def run_all_cleanups():
    """Fonction principale appelée par le planificateur (schedule)."""
    # Nettoyage local désactivé à la demande de l'utilisateur (conservation à vie)
    # cleanup_local_images()
    cleanup_firebase_storage()
