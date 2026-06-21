import asyncio
import websockets
import json
import logging
from .config import EUFY_WS_URL

logger = logging.getLogger("EufyClient")

class EufyClient:
    def __init__(self, ws_url: str = EUFY_WS_URL, image_callback=None):
        self.ws_url = ws_url
        self.reconnect_delay = 30
        self.is_running = False
        self.image_callback = image_callback
        self.ws = None
        self.is_streaming = False
        self.h264_file = None
        self.h264_path = None
        self.is_connected = False

    async def connect_and_listen(self):
        self.is_running = True
        
        while self.is_running:
            try:
                logger.info(f"Tentative de connexion Eufy WebSocket à {self.ws_url}...")
                async with websockets.connect(self.ws_url) as websocket:
                    logger.info("Connexion WebSocket établie avec succès !")
                    self.ws = websocket
                    self.is_connected = True
                    
                    # Commande OBLIGATOIRE pour activer les commandes récentes
                    await websocket.send(json.dumps({
                        "messageId": "set_schema",
                        "command": "set_api_schema",
                        "schemaVersion": 21
                    }))
                    
                    # Commande OBLIGATOIRE pour que le pont envoie les événements
                    await websocket.send(json.dumps({
                        "messageId": "start_listening",
                        "command": "start_listening"
                    }))
                    
                    while self.is_running:
                        message = await websocket.recv()
                        await self.handle_message(message)
                        
            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
                logger.warning(f"Connexion WebSocket Eufy perdue/refusée : {e}")
            except Exception as e:
                logger.error(f"Erreur Eufy : {e}")
            finally:
                self.is_connected = False
            
            if self.is_running:
                logger.info(f"Reconnexion Eufy dans {self.reconnect_delay} secondes...")
                await asyncio.sleep(self.reconnect_delay)

    async def stop_livestream_after_delay(self, serial_number, delay):
        await asyncio.sleep(delay)
        logger.info("Fin de l'enregistrement vidéo P2P. Arrêt du flux...")
        if self.ws:
            await self.ws.send(json.dumps({
                "messageId": "stop_live",
                "command": "device.stop_livestream",
                "serialNumber": serial_number
            }))
        self.is_streaming = False
        if self.h264_file:
            self.h264_file.close()
            self.h264_file = None
            
        # Appel de l'IA avec le chemin du fichier .h264
        if self.image_callback and self.h264_path:
            logger.info("Déclenchement du callback IA avec le fichier vidéo H264...")
            await self.image_callback(self.h264_path)

    async def handle_message(self, message: str):
        try:
            data = json.loads(message)
            
            if data.get("type") == "result":
                logger.info(f"Réponse Eufy : {str(data)[:200]}")
                
            elif data.get("type") == "event":
                event_data = data.get("event", {})
                event_name = event_data.get("event")
                
                # Filtrer les logs superflus
                if "livestream video data" not in str(event_name) and "livestream audio data" not in str(event_name):
                    logger.info(f"Événement Eufy reçu : {event_name}")

                if event_name == "motion detected":
                    logger.info("🚨 Mouvement Eufy détecté !")
                    serial_number = event_data.get("serialNumber")
                    
                    if serial_number and not self.is_streaming and self.ws:
                        logger.info(f"Lancement de l'enregistrement P2P pour {serial_number}...")
                        self.is_streaming = True
                        
                        # Création du fichier vidéo
                        from core.config import IMAGES_DIR
                        self.h264_path = str(IMAGES_DIR.parent / "stream.h264")
                        self.h264_file = open(self.h264_path, "wb")
                        
                        # Lancement du livestream
                        await self.ws.send(json.dumps({
                            "messageId": "start_live",
                            "command": "device.start_livestream",
                            "serialNumber": serial_number
                        }))
                        
                        # Programmation de l'arrêt (3 secondes de clip)
                        asyncio.create_task(self.stop_livestream_after_delay(serial_number, 5.0))

                elif event_name in ["livestream video data", "livestream video data payload"] and self.is_streaming:
                    buffer_dict = event_data.get("buffer", {})
                    # Dans le pont Eufy, les données sont souvent dans buffer.data (tableau d'octets)
                    buffer_data = buffer_dict.get("data", [])
                    if self.h264_file and buffer_data:
                        self.h264_file.write(bytes(buffer_data))
                
        except json.JSONDecodeError:
            pass

    def stop(self):
        self.is_running = False
        logger.info("Arrêt du client Eufy...")
