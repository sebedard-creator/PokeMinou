# Changelog - PokeMinou

Toutes les modifications notables apportées à ce projet seront documentées dans ce fichier.

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
