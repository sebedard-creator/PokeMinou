# Handoff - PokeMinou

## Ce qui a été accompli (Dernière session)
- **Multi-Caméras Parfait** : Le système surveille simultanément et avec succès plusieurs caméras Eufy via leurs liens RTSP déclarés dans `RTSP_URLS`. La HomeBase limite à un seul identifiant global par système, ce qui a été documenté.
- **Résolution des crashs IA et FFMPEG (Robustesse Maximale)** :
  - **ProcessLookupError** : Correction d'un crash lorsque `ffmpeg` se terminait à la milliseconde près du timeout imposé.
  - **Framerate Variable** : L'IA ignore désormais dynamiquement les premiers 30% d'une vidéo (au lieu de 45 frames codées en dur). Cela permet aux caméras qui filment à très bas FPS d'être analysées avec succès.
  - **Auto-Retry & Arrêt Propre** : Si la capture d'un flux échoue (vidéo vide ou timeout), le radar effectue automatiquement une 2e tentative de capture après 1 seconde. Ffmpeg est maintenant arrêté proprement par le signal clavier `q` (au lieu d'un `kill` Windows abrupt) pour préserver l'index des fichiers MP4 fragmentés.
  - **Détection défensive** : Le coeur du moniteur asynchrone est enveloppé dans des blocs try-except robustes pour garantir que même si un double échec de capture survient, le programme général ne se fige jamais et continue la détection.
  - **Journalisation FFMPEG** : Les logs détaillés d'erreurs de ffmpeg sont capturés pour diagnostic en cas de corruption de flux.
- **Autonomie Python & Nettoyage** : Le vieux système de `.bat` complexes a été rasé. L'application utilise maintenant `python-dotenv` pour charger ses secrets, et se lance d'un simple `start.bat`.

## État actuel du système
- Le système backend Python est **entièrement stable** et opérationnel.
- L'interface d'administration Gradio est fonctionnelle.
- L'intégration Android/Firebase pour les notifications Push est prête et configurée.
- **Aucun mot de passe ni clé d'API** n'est codé en dur. Les règles de sécurité sont à 100% respectées, le fichier `.env` et le `serviceAccountKey.json` sont protégés par le `.gitignore`.

## Prochaines étapes suggérées pour le développeur
- Poursuivre le développement matériel (ex: ajout de servos MG90S pour un projet de distributeur de croquettes ou de tourelle, tel qu'évoqué précédemment).
- Tester le système en conditions réelles avec le chat sur plusieurs jours.
