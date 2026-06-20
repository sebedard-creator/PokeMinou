import firebase_admin
from firebase_admin import credentials, storage, messaging
import logging
from pathlib import Path
import os
from core.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_STORAGE_BUCKET

logger = logging.getLogger("FirebaseSync")

class FirebaseManager:
    def __init__(self):
        self.is_initialized = False
        self._init_firebase()

    def _init_firebase(self):
        if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
            logger.warning(f"Fichier Firebase introuvable ({FIREBASE_CREDENTIALS_PATH}). Les notifications Push sont désactivées.")
            return

        try:
            cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
            # On vérifie si l'app par défaut n'est pas déjà initialisée
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': FIREBASE_STORAGE_BUCKET
                })
            self.is_initialized = True
            logger.info("Firebase initialisé avec succès.")
        except Exception as e:
            logger.error(f"Erreur d'initialisation Firebase : {e}")

    def upload_image_to_storage(self, local_image_path: str) -> str:
        """Upload l'image sur Firebase Storage et retourne l'URL publique."""
        if not self.is_initialized:
            logger.warning("Firebase non initialisé. Impossible d'uploader l'image.")
            return None

        try:
            bucket = storage.bucket()
            blob_name = f"cats/{Path(local_image_path).name}"
            blob = bucket.blob(blob_name)
            
            logger.info(f"Upload de {local_image_path} vers Storage...")
            blob.upload_from_filename(local_image_path)
            
            # Rendre le fichier publiquement accessible pour qu'Android puisse le télécharger
            blob.make_public()
            public_url = blob.public_url
            logger.info(f"Upload réussi. URL publique : {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Erreur lors de l'upload Firebase Storage : {e}")
            return None

    def send_push_notification(self, cat_name: str, image_url: str):
        """Envoie un message FCM (Push) à l'application Android."""
        if not self.is_initialized:
            return

        try:
            # Envoi à tous les appareils abonnés au topic "all"
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Minou Détecté!",
                    body=f"{cat_name}",
                    image=image_url if image_url else None
                ),
                data={
                    "cat_name": str(cat_name),
                    "image_url": str(image_url) if image_url else ""
                },
                topic="all"
            )
            response = messaging.send(message)
            logger.info(f"Message FCM envoyé avec succès : {response}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message FCM : {e}")

# Instance globale (Singleton pattern simplifié)
firebase_mgr = FirebaseManager()
