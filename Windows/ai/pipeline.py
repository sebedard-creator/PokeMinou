import cv2
import numpy as np
from PIL import Image
import logging
from ultralytics import YOLO
import io
import time
from datetime import datetime
from pathlib import Path
import asyncio

from core.config import YOLO_MODEL_PATH, CAT_CLASS_ID, CONFIDENCE_THRESHOLD, IMAGES_DIR, COSINE_SIMILARITY_THRESHOLD, RTSP_URL
from ai.reid import CatReID
from db.database import DBManager
from cloud.firebase_sync import firebase_mgr

logger = logging.getLogger("AIPipeline")

class AIPipeline:
    def __init__(self, db_manager: DBManager):
        logger.info("Initialisation du pipeline IA (YOLOv8 + ReID)...")
        # Téléchargera automatiquement yolov8n.pt la première fois
        self.yolo = YOLO('yolov8n.pt') 
        self.reid = CatReID()
        self.db = db_manager

    def is_image_color(self, img_np: np.ndarray, saturation_threshold: int = 15) -> bool:
        """Détermine si l'image est de jour (Couleur) ou de nuit (IR/Niveaux de gris)."""
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        mean_saturation = np.mean(hsv[:, :, 1])
        logger.info(f"Saturation moyenne de l'image : {mean_saturation:.2f}")
        return mean_saturation > saturation_threshold

    async def process_image(self, picture_bytes_or_path=None):
        """
        Traitement principal de l'image (depuis P2P H264 ou image de test).
        """
        logger.info("Démarrage de la séquence IA...")
        
        if picture_bytes_or_path is None:
            logger.error("Aucune source d'image fournie.")
            return
            
        img = None
        best_box = None
        cat_found = False
        import core.config as config

        if isinstance(picture_bytes_or_path, str) and picture_bytes_or_path.endswith('.h264'):
            logger.info(f"Extraction d'une frame HD depuis le clip vidéo : {picture_bytes_or_path}")
            cap = cv2.VideoCapture(picture_bytes_or_path)
            if cap.isOpened():
                valid_frames = []
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    valid_frames.append(frame)
                cap.release()
                
                if valid_frames:
                    logger.info("Analyse des frames vidéo à la recherche d'un chat...")
                    start_idx = min(5, len(valid_frames) - 1)
                    
                    for i in range(start_idx, len(valid_frames), 5):
                        test_img = valid_frames[i]
                        results = self.yolo.predict(test_img, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
                        
                        for result in results:
                            for box in result.boxes:
                                if int(box.cls[0]) == CAT_CLASS_ID:
                                    cat_found = True
                                    best_box = box.xyxy[0].cpu().numpy().astype(int)
                                    img = test_img
                                    break
                            if cat_found: break
                            
                        if cat_found:
                            logger.info(f"🐱 Chat détecté avec succès à la frame {i} !")
                            break

                    if not cat_found:
                        logger.info("Aucun chat détecté sur l'ensemble du clip. Image ignorée.")
                        return
                        
                    # Sauvegarde pour le débogage visuel
                    from core.config import IMAGES_DIR
                    debug_path = str(IMAGES_DIR.parent / "last_frame.jpg")
                    cv2.imwrite(debug_path, img)
                else:
                    logger.error("Le clip vidéo est vide ou illisible.")
                    return
            else:
                logger.error("Impossible d'ouvrir le fichier vidéo .h264.")
                return
        else:
            # Traitement d'une image classique (test manuel)
            if isinstance(picture_bytes_or_path, bytes):
                nparr = np.frombuffer(picture_bytes_or_path, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = cv2.imread(picture_bytes_or_path)

            if img is None:
                logger.error("Impossible d'obtenir l'image statique.")
                return

            results = self.yolo.predict(img, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
            for result in results:
                for box in result.boxes:
                    if int(box.cls[0]) == CAT_CLASS_ID:
                        cat_found = True
                        best_box = box.xyxy[0].cpu().numpy().astype(int)
                        break
                if cat_found: break

            if not cat_found:
                logger.info("Aucun chat détecté sur l'image statique.")
                return

        # 2. Recadrage (Cropping)
        x1, y1, x2, y2 = best_box
        cropped_img_cv = img[y1:y2, x1:x2]
        
        # 3. Vérification Jour / Nuit
        is_day = self.is_image_color(cropped_img_cv)
        
        identified_cat_id = None
        identified_cat_name = "Inconnu"
        
        # Sauvegarde locale de l'image croppée
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_img_path = str(IMAGES_DIR / f"cat_{timestamp}.jpg")
        cv2.imwrite(saved_img_path, cropped_img_cv)
        
        if not is_day:
            logger.info("Image détectée comme NOCTURNE (Infrarouge). ID générique attribué.")
            # Chercher l'ID de "Chat_Nuit_Mystere" dans la DB
            cats = self.db.get_all_cats()
            for cat in cats:
                if cat["name"] == "Chat_Nuit_Mystere":
                    identified_cat_id = cat["id"]
                    identified_cat_name = cat["name"]
                    break
        else:
            logger.info("Image détectée comme DIURNE. Extraction des features ReID...")
            # Convertir BGR (OpenCV) en RGB (PIL) pour ReID
            cropped_img_rgb = cv2.cvtColor(cropped_img_cv, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cropped_img_rgb)
            
            # Extraction
            current_embedding = self.reid.extract_features(pil_image)
            
            # Comparaison avec la DB
            db_cats = self.db.get_all_cats()
            best_match_id = None
            best_match_name = None
            best_score = 0.0
            
            for cat in db_cats:
                if cat["embedding"] is not None and cat["name"] != "Chat_Nuit_Mystere":
                    score = self.reid.cosine_similarity(current_embedding, cat["embedding"])
                    if score > best_score:
                        best_score = score
                        best_match_id = cat["id"]
                        best_match_name = cat["name"]
            
            logger.info(f"Meilleur score de similarité : {best_score:.2f} (Seuil: {COSINE_SIMILARITY_THRESHOLD})")
            
            if best_score >= COSINE_SIMILARITY_THRESHOLD:
                identified_cat_id = best_match_id
                identified_cat_name = best_match_name
                logger.info(f"Chat identifié : {identified_cat_name} (ID: {identified_cat_id})")
            else:
                logger.info("Aucun chat connu correspondant. Création d'un profil temporaire...")
                identified_cat_name = f"Nouveau_{timestamp}"
                identified_cat_id = self.db.add_or_update_cat(identified_cat_name, current_embedding)
                
        # 4. Enregistrement de la visite
        if identified_cat_id is not None:
            # Vérification du Cooldown AVANT d'enregistrer la nouvelle visite
            can_send_push = self.db.check_cooldown(identified_cat_id)
            
            self.db.log_visit(identified_cat_id, saved_img_path)
            if can_send_push:
                logger.info("Cooldown OK. Prêt pour Firebase Push !")
                # Upload sur Storage
                public_url = firebase_mgr.upload_image_to_storage(saved_img_path)
                # Envoi du FCM Push
                firebase_mgr.send_push_notification(identified_cat_name, public_url)
            else:
                logger.info("Notification Push bloquée (Cooldown actif).")
