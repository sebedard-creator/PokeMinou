# Changelog - PokeMinou

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

## [1.0.0-dev.2] - 2026-06-20
### Changé
- **Pivot Android :** Migration des scripts de build de Kotlin (KTS) vers Groovy et mise à jour de l'Android Gradle Plugin (AGP) en 8.3.0 pour résoudre les erreurs de configuration `debugCompileClasspath`.
- **Firebase FCM :** Ajout du support du "Data Payload" dans le backend Python pour envoyer l'URL de l'image et le nom du chat.
- **Android UI :** Réécriture de `MainActivity.kt` pour intercepter le Data Payload en arrière-plan et afficher l'image reçue en HD via Coil (`CatDetectedScreen`).
- **Cooldown Dynamique :** Lecture en temps réel du seuil de cooldown depuis la configuration modifiée via l'interface Gradio (au lieu d'une copie statique à l'initialisation).
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
