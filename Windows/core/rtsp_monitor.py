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
        
        # Décalage de démarrage pour éviter que les deux radars ne pingent la HomeBase
        # exactement à la même milliseconde (ce qui peut causer une erreur 401)
        try:
            delay = int(self.camera_id) * 0.5
            await asyncio.sleep(delay)
        except ValueError:
            pass
            
        
        while self.is_running:
            is_awake = await self._ping_rtsp()

            if is_awake and not self.is_motion_active:
                self.is_motion_active = True
                self.logger.info("🚨 [MOUVEMENT] Caméra réveillée ! Démarrage de la capture vidéo ffmpeg...")
                try:
                    await self._record_stream()
                except Exception as e:
                    self.logger.error(f"Erreur inattendue lors de l'exécution de la capture : {e}")
            elif not is_awake and self.is_motion_active:
                self.is_motion_active = False
                self.logger.info("💤 [FIN DE MOUVEMENT] La caméra s'est rendormie.")
            
            # Attendre avant le prochain ping
            await asyncio.sleep(self.ping_interval)

    async def _record_stream(self):
        """Lance ffmpeg pour capturer le flux RTSP dans un .mp4 avec logique de réessai."""
        output_file = str(IMAGES_DIR.parent / f"stream_Cam{self.camera_id}.mp4")
        log_file_path = str(IMAGES_DIR.parent / f"ffmpeg_Cam{self.camera_id}.log")
        
        max_attempts = 2
        success = False
        
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                self.logger.info(f"🔄 Nouvelle tentative de capture dans 1 seconde... (Tentative {attempt}/{max_attempts})")
                await asyncio.sleep(1.0)
            
            # Ouvrir le fichier de log ffmpeg en mode écriture (écrase le log précédent)
            try:
                log_file = open(log_file_path, "w", encoding="utf-8")
            except Exception as e:
                # Si erreur d'ouverture du log, on utilise DEVNULL pour ne pas bloquer
                self.logger.warning(f"Impossible d'ouvrir le fichier de log ffmpeg : {e}")
                log_file = asyncio.subprocess.DEVNULL
                
            self.logger.info("Démarrage de la capture vidéo ffmpeg...")
            
            # Commande ffmpeg robuste :
            # -rtsp_transport tcp : Force le protocole TCP
            # -timeout 5000000 : Timeout de 5s au niveau socket
            # -movflags frag_keyframe+empty_moov+default_base_moof : MP4 fragmenté (résistant aux crashs)
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-y', 
                '-rtsp_transport', 'tcp',
                '-timeout', '5000000',
                '-i', self.rtsp_url, 
                '-c', 'copy', 
                '-t', '10', 
                '-movflags', 'frag_keyframe+empty_moov+default_base_moof',
                output_file,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=log_file
            )
            
            # Si on a ouvert un fichier log, on le ferme côté Python (le processus enfant en garde une copie pour écrire)
            if log_file != asyncio.subprocess.DEVNULL:
                log_file.close()
                
            try:
                # On attend la fin de ffmpeg (timeout de sécurité de 15s)
                await asyncio.wait_for(process.wait(), timeout=15.0)
                
                # Vérifier si le fichier existe et n'est pas vide
                if os.path.exists(output_file) and os.path.getsize(output_file) > 5000:
                    success = True
                    self.logger.info(f"✅ [CAPTURE TERMINÉE] Fichier sauvegardé sous stream_Cam{self.camera_id}.mp4.")
                else:
                    self.logger.warning(f"Fichier de capture invalide ou trop petit ({os.path.getsize(output_file) if os.path.exists(output_file) else 0} octets).")
            except asyncio.TimeoutError:
                self.logger.warning("Ffmpeg a dépassé le délai maximum de 15s. Tentative d'arrêt propre...")
                if process.stdin:
                    try:
                        process.stdin.write(b'q\n')
                        await process.stdin.drain()
                        # Attendre 2.0s que ffmpeg s'arrête proprement
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                        if os.path.exists(output_file) and os.path.getsize(output_file) > 5000:
                            success = True
                            self.logger.info("Ffmpeg arrêté proprement. Vidéo exploitable récupérée.")
                    except Exception as exc:
                        self.logger.warning(f"Échec de l'arrêt propre, forçage de l'extinction : {exc}")
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
            except Exception as e:
                self.logger.error(f"Erreur durant l'exécution de ffmpeg : {e}")
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            
            if success:
                break
                
        # Déclenchement de l'IA
        if success:
            if self.image_callback:
                self.logger.info("Déclenchement de l'analyse IA sur le fichier mp4...")
                asyncio.create_task(self.image_callback(output_file))
        else:
            self.logger.error("Impossible de récupérer un flux vidéo valide après toutes les tentatives de réessai.")

    def stop(self):
        self.is_running = False
        self.logger.info("Arrêt du radar RTSP...")
