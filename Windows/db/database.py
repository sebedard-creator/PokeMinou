import sqlite3
import numpy as np
import logging
from datetime import datetime, timedelta
from pathlib import Path
import core.config as config

logger = logging.getLogger("Database")

class DBManager:
    def __init__(self):
        self.db_path = config.DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialise les tables de la base de données si elles n'existent pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table Cats: ID, Nom, Vecteur (Embedding stocké en binaire ou JSON)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Cats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                embedding BLOB
            )
        ''')
        
        # Table Visits: Lien vers Cats, Timestamp de la visite, et chemin de la photo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cat_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                FOREIGN KEY(cat_id) REFERENCES Cats(id)
            )
        ''')
        
        # Insertion d'un profil générique pour la nuit si non existant
        cursor.execute("SELECT id FROM Cats WHERE name = 'Chat_Nuit_Mystere'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Cats (name) VALUES ('Chat_Nuit_Mystere')")
            
        conn.commit()
        conn.close()
        logger.info(f"Base de données SQLite initialisée à {self.db_path}")

    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Convertit un array Numpy (vecteur ReID) en bytes pour SQLite."""
        return embedding.tobytes() if embedding is not None else None

    def deserialize_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """Convertit les bytes de SQLite en array Numpy (float32 attendu)."""
        if embedding_bytes is None:
            return None
        return np.frombuffer(embedding_bytes, dtype=np.float32)

    def get_all_cats(self):
        """Récupère tous les profils de chats (utilisé par ReID et Gradio)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, embedding FROM Cats")
        rows = cursor.fetchall()
        conn.close()
        
        cats = []
        for row in rows:
            cats.append({
                "id": row[0],
                "name": row[1],
                "embedding": self.deserialize_embedding(row[2])
            })
        return cats

    def add_or_update_cat(self, name: str, embedding: np.ndarray = None, cat_id: int = None):
        """Crée ou met à jour le profil d'un chat (nom et/ou embedding)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        emb_bytes = self.serialize_embedding(embedding)
        
        if cat_id:
            cursor.execute("UPDATE Cats SET name = ?, embedding = ? WHERE id = ?", (name, emb_bytes, cat_id))
        else:
            cursor.execute("INSERT INTO Cats (name, embedding) VALUES (?, ?)", (name, emb_bytes))
            cat_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        logger.info(f"Profil chat '{name}' mis à jour/ajouté (ID: {cat_id})")
        return cat_id

    def log_visit(self, cat_id: int, image_path: str):
        """Enregistre une visite dans la DB."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Visits (cat_id, image_path) VALUES (?, ?)", (cat_id, image_path))
        conn.commit()
        conn.close()
        logger.info(f"Visite enregistrée pour cat_id: {cat_id}")

    def check_cooldown(self, cat_id: int) -> bool:
        """
        Vérifie si la dernière visite du chat est plus ancienne que le COOLDOWN.
        Retourne True si c'est bon (la notif peut être envoyée), False sinon (spam).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupère la dernière visite du chat
        cursor.execute('''
            SELECT timestamp FROM Visits 
            WHERE cat_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (cat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            last_visit_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.utcnow() - last_visit_time
            if time_diff < timedelta(minutes=config.COOLDOWN_MINUTES):
                logger.info(f"Cooldown actif pour le chat ID {cat_id} ({time_diff.seconds//60} min écoulées).")
                return False # On bloque la notif Push
        
        return True # OK pour envoyer la notif
