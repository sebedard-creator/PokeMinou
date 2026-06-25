import asyncio
import logging
import base64
import os
import urllib.parse
from core.config import IMAGES_DIR

logger = logging.getLogger("RTSPMonitor")

class RTSPMonitor:
    def __init__(self, url, camera_id="1", image_callback=None):
        self.rtsp_url = url
        self.camera_id = camera_id
        self.image_callback = image_callback
        self.logger = logging.getLogger(f"RTSPMonitor-Cam{self.camera_id}")
        self.is_running = False
        self.is_motion_active = False
        self.ping_interval = 2.0  # secondes

        # Parser l'URL RTSP
        try:
            parsed = urllib.parse.urlparse(self.rtsp_url)
            self.host = parsed.hostname
            self.port = parsed.port if parsed.port else 554
            self.path = parsed.path
            self.username = parsed.username
            self.password = parsed.password
            
            # Auth header pour la HomeBase Eufy
            auth_str = f"{self.username}:{self.password}"
            b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
            self.auth_header = f"Authorization: Basic {b64_auth}"
            self.clean_url = f"rtsp://{self.host}:{self.port}{self.path}"
        except Exception as e:
            self.logger.error(f"Erreur de parsing RTSP_URL : {e}")
            self.host = None

    async def _ping_rtsp(self):
        """Envoie un TCP ping (DESCRIBE) à la caméra pour vérifier son état d'éveil."""
        if not self.host:
            return False

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), 
                timeout=2.0
            )
            
            request = f"DESCRIBE {self.clean_url} RTSP/1.0\r\nCSeq: 1\r\nAccept: application/sdp\r\n{self.auth_header}\r\n\r\n"
            writer.write(request.encode('utf-8'))
            await writer.drain()

            data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
            writer.close()
            await writer.wait_closed()

            response = data.decode('utf-8', errors='ignore')
            first_line = response.split('\r\n')[0]
            
            if "200 OK" in first_line:
                return True
            elif "401" in first_line:
                self.logger.error("Erreur 401 : Identifiants RTSP refusés.")
                return False
            else:
                return False

        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False
        except Exception as e:
            return False

    async def connect_and_listen(self):
        self.is_running = True
        self.logger.info(f"Démarrage du radar local RTSP sur : {self.host}:{self.port}{self.path}")
        
        while self.is_running:
            is_awake = await self._ping_rtsp()

            if is_awake and not self.is_motion_active:
                self.is_motion_active = True
                self.logger.info("🚨 [MOUVEMENT] Caméra réveillée ! Démarrage de la capture vidéo ffmpeg...")
                await self._record_stream()
            elif not is_awake and self.is_motion_active:
                self.is_motion_active = False
                self.logger.info("💤 [FIN DE MOUVEMENT] La caméra s'est rendormie.")
            
            # Attendre avant le prochain ping
            await asyncio.sleep(self.ping_interval)

    async def _record_stream(self):
        """Lance ffmpeg pour capturer le flux RTSP dans un .mp4."""
        output_file = str(IMAGES_DIR.parent / f"stream_Cam{self.camera_id}.mp4")
        
        # Commande ffmpeg (capture brute sans ré-encodage, limité à 10 secondes pour garantir un clip rapide)
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', 
            '-i', self.rtsp_url, 
            '-c', 'copy', 
            '-t', '10',  # Force l'arrêt après 10 secondes pour analyser rapidement
            output_file,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        # On attend la fin de ffmpeg (timeout de sécurité de 15s)
        try:
            await asyncio.wait_for(process.wait(), timeout=15.0)
            self.logger.info(f"✅ [CAPTURE TERMINÉE] Fichier sauvegardé sous stream_Cam{self.camera_id}.mp4.")
        except asyncio.TimeoutError:
            process.kill()
            self.logger.warning("Ffmpeg a été interrompu après le délai maximum.")
            
        # Déclenchement de l'IA
        if self.image_callback:
            self.logger.info("Déclenchement de l'analyse IA sur le fichier mp4...")
            # On lance la tâche en arrière-plan pour ne pas bloquer le radar
            asyncio.create_task(self.image_callback(output_file))

    def stop(self):
        self.is_running = False
        self.logger.info("Arrêt du radar RTSP...")
