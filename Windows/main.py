import asyncio
import logging
import threading
import time
import schedule

from core.rtsp_monitor import RTSPMonitor
from db.database import DBManager
from ai.pipeline import AIPipeline
from ui.admin_app import start_gradio
from utils.cleaner import run_all_cleanups

# Configuration du logging principal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")

def run_schedule():
    """Exécute les tâches planifiées en arrière-plan."""
    while True:
        schedule.run_pending()
        time.sleep(60)

async def main():
    logger.info("Démarrage du système PokeMinou Backend...")
    
    # 1. Tâches planifiées (Nettoyage DB, Images, etc.) chaque jour à 03:00
    schedule.every().day.at("03:00").do(run_all_cleanups)
    
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    
    # 2. Initialiser la DB et l'IA
    db_manager = DBManager()
    ai_pipeline = AIPipeline(db_manager)
    
    # 3. Initialiser les radars RTSP pour chaque URL configurée
    from core.config import RTSP_URLS
    
    monitors = []
    for idx, url in enumerate(RTSP_URLS, start=1):
        monitor = RTSPMonitor(url=url, camera_id=str(idx), image_callback=ai_pipeline.process_image)
        monitors.append(monitor)
    
    if not monitors:
        logger.error("Aucune URL RTSP configurée. Veuillez vérifier le fichier .env.")
        return
        
    # 4. Lancer l'interface Web d'administration Gradio
    start_gradio(db_manager, monitors)
    
    # Lancement de la boucle de surveillance pour tous les radars (bloquant)
    await asyncio.gather(*(m.connect_and_listen() for m in monitors))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Arrêt manuel du système.")
