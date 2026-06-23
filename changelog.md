# Changelog - PokeMinou

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [1.0.0-dev.3] - 2026-06-21
### Changé
- **Extraction Vidéo IA :** Refonte majeure de `process_image()`. L'IA ne se contente plus de lire aveuglément la 10ème frame, mais elle scanne l'intégralité du clip vidéo (1 frame sur 5) jusqu'à ce qu'elle trouve une détection positive d'un chat. Cela garantit une capture fiable même si le chat est furtif ou en mouvement rapide.
- **Interface UI Gradio :** Les valeurs des paramètres (Confiance et Cooldown) utilisent désormais une évaluation dynamique (`lambda`) pour toujours afficher la valeur réelle en RAM lors d'un rafraîchissement de la page (F5), contrant ainsi le cache persistant de Gradio.

### Corrigé
- **Bug YOLO :** Correction du système de configuration où YOLO lisait le seuil de confiance (`CONFIDENCE_THRESHOLD`) de façon statique lors de l'initialisation. Il interroge désormais le module dynamiquement à chaque prédiction.
- **Paramètres Amnésiques :** Ajout d'une véritable persistance des paramètres modifiés via le Dashboard Gradio. Les valeurs sont maintenant sauvegardées dans `data/settings.json` et rechargées au redémarrage du serveur.
- **UI Galerie :** Correction du confinement artificiel de l'interface (`max-width: 1200px` désactivé) et ajout de la gestion adaptative de la hauteur de la galerie (`85vh`) pour un affichage plein écran sans écrasement vertical des images.
- **Crash de Lancement Silencieux (Locks) :** Refonte de la chaîne de lancement (`StartPokeMinou.vbs`, `start_silent.bat`, `system_engine.bat`). Résolution des problèmes de guillemets Windows et de variables PATH en utilisant le nom court `PROGRA~1` et un sous-script `run_node.bat`. 
- **Processus Zombies :** Mise à jour majeure de `stop.bat` pour détecter et tuer les processus `cmd.exe` orphelins qui verrouillaient les fichiers de log (`startup.log`) et empêchaient le redémarrage.

### Ajouté
- **Indicateur d'État Eufy :** Intégration d'un témoin visuel 🟢/🔴 dans l'interface d'administration Gradio pour suivre l'état de connexion en temps réel entre le script Python et le pont Node.js (`eufy-security-ws`).

## [1.0.0-dev.2] - 2026-06-20
### Changé
- **Pivot Android :** Migration des scripts de build de Kotlin (KTS) vers Groovy et mise à jour de l'Android Gradle Plugin (AGP) en 8.3.0 pour résoudre les erreurs de configuration `debugCompileClasspath`.
- **Firebase FCM :** Ajout du support du "Data Payload" dans le backend Python pour envoyer l'URL de l'image et le nom du chat.
- **Android UI :** Réécriture de `MainActivity.kt` pour intercepter le Data Payload en arrière-plan et afficher l'image reçue en HD via Coil (`CatDetectedScreen`). Remplacement de `ContentScale.Crop` par `ContentScale.Fit` pour afficher l'image du chat en entier sans la tronquer.
- **Android Manifest :** Ajout de `android:launchMode="singleTop"` pour forcer l'appel de `onNewIntent` et régler un bug de réception de payload sur certains téléphones (Samsung, Xiaomi, etc.).
- **Cooldown Dynamique :** Lecture en temps réel du seuil de cooldown depuis la configuration modifiée via l'interface Gradio (au lieu d'une copie statique à l'initialisation).
- **Extraction Vidéo IA :** Optimisation de la capture P2P pour contrer le délai de connexion de la caméra. L'IA extrait désormais la 10ème frame (au lieu du premier tiers) pour flasher le chat au plus vite.
- **Nettoyage :** Désactivation du nettoyage des images locales (conservation à vie de la base SQLite et des images locales sur disque). Le nettoyage Firebase (48h) est maintenu.
- **Dépendances :** Suppression de la dépendance orpheline `huggingface_hub` de `requirements.txt`.

### Corrigé
- **Bug Timezone :** Correction du système de cooldown. Utilisation de `datetime.utcnow()` en Python pour correspondre aux timestamps UTC insérés par SQLite (`CURRENT_TIMESTAMP`), évitant un blocage permanent des notifications.

### Ajouté
- **Sécurité :** Sécurisation complète des `.gitignore` pour le dossier Root, Windows et Android (Exclusion stricte des clés Eufy, Firebase, et dossiers de données).
- **Documentation :** Création d'un `README.md` exhaustif en anglais expliquant l'écosystème.
- **Scripts utilitaires :** Création de `StartPokeMinou.vbs` pour permettre le lancement du backend en arrière-plan (silencieux) via le dossier de démarrage Windows.
## [1.0.0-dev.1] - 2026-06-19
### Ajouté
- Initialisation du projet.
- Création du `changelog.md`.
- Mise à jour du prompt maître (`pokeminou.md`) avec la règle de préparation pour GitHub (`.gitignore`).
- Création de l'arborescence pour le module Windows.
- Création de l'environnement virtuel (`venv`), `.gitignore` et `requirements.txt`.
- Implémentation des modules `core/config.py`, `core/eufy_ws.py` et `main.py`.
- Implémentation du module `db/database.py` avec la gestion SQLite et la logique de Cooldown.
- Implémentation du pipeline IA `ai/pipeline.py` (YOLOv8 + Vérification Jour/Nuit).
- Implémentation du module `ai/reid.py` (ResNet50 + Similarité Cosinus).
- Implémentation de l'interface d'administration web `ui/admin_app.py` avec Gradio (Thème sombre premium, réglages et galerie).
- Implémentation de `cloud/firebase_sync.py` pour l'upload Storage et l'envoi des notifications Push FCM.
- Implémentation de `utils/cleaner.py` pour supprimer les images obsolètes (local > 30j, Firebase > 48h) via une tâche planifiée dans `main.py`.
- Ajout de `start.bat` et `stop.bat` à la racine pour faciliter le lancement et l'arrêt du serveur local.
- Installation locale du pont WebSockets `eufy-security-ws` via npm et création du script `start_bridge.bat` pour le lancement.
