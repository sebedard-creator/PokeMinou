# Prompt Maître : Système de Sécurité et Pokedex Félin

**Rôle :** Agis en tant que Développeur Senior Full-Stack et Ingénieur en Vision par Ordinateur. 

**Objectif :** M'accompagner dans la création d'un système de sécurité et de reconnaissance faciale féline sur mesure. Le projet est divisé en deux parties : un backend Python local et une application Android native en Kotlin.

Voici l'architecture complète et le cahier des charges strict du projet. Ton objectif pour cette première requête est d'analyser cette architecture, de me proposer la structure des fichiers (arborescence) et de me générer le code du module de base (Backend Python). Nous ferons l'application Kotlin dans un second temps.

---

## CONTEXTE MATÉRIEL
* **Capteur :** Eufy Cam 2C fonctionnant sur batterie.
* **Contrainte stricte :** AUCUN flux vidéo continu (RTSP) pour préserver la batterie. L'application doit réagir uniquement aux événements de mouvement générés par le capteur PIR de la camera.

---

## 1. LE BACKEND PYTHON (Serveur Local)
Ce script tournera en permanence comme un service (avec Watchdog/Auto-restart) sur mon PC local.

### A. Écoute de l'API (eufy-security-ws)
* Le script Python doit se connecter à un pont WebSockets `eufy-security-ws` en local.
* Il écoute les événements de détection de mouvement.
* **Résilience :** Le code doit inclure un bloc `try/except` très robuste. Si le WebSocket coupe, le script doit tenter de se reconnecter indéfiniment (délai de 30 secondes) sans faire crasher le reste de l'application.

### B. Le Pipeline d'Intelligence Artificielle
Lorsqu'une image est reçue via l'événement Eufy, elle passe par ce flux :
1. **Détection (YOLOv8) :** Utiliser `ultralytics` (`yolov8n.pt`). Vérifier si la classe "cat" (15) est présente.
2. **Recadrage :** Rogner (cropper) l'image au plus près de la "bounding box" du chat pour éliminer le décor.
3. **Vérification Jour/Nuit :** Analyser la saturation de l'image recadrée. Si l'image est en niveaux de gris (Infrarouge), on saute la ré-identification, on attribue l'ID générique "Chat_Nuit_Mystere" et on passe à la notification.
4. **Ré-Identification (ReID) :** Si l'image est en couleur, passer l'image recadrée dans un modèle d'extraction de caractéristiques (ex: ResNet ou Siamese) pour générer un vecteur mathématique. Comparer ce vecteur avec la base de données via similarité cosinus pour trouver l'ID du chat (ex: "Garfield").

### C. Base de Données & Logique (SQLite)
* Créer une base de données locale contenant les tables : `Cats` (ID, Nom, Vecteur de référence) et `Visits` (Cat_ID, Timestamp, Image_Path).
* **Cooldown individuel :** Le système doit vérifier à quand remonte la dernière visite de ce chat spécifique. Si c'est inférieur au délai paramétré (défaut : 10 minutes), on sauvegarde l'événement dans la DB mais on BLOQUE l'envoi de la notification Push.

### D. Interface Web d'Administration (Gradio)
* Créer une interface locale via `gradio` (ex: port 8095).
* **Fonctionnalités :** * Curseurs pour modifier le seuil de confiance YOLO et la durée du cooldown.
  * Galerie affichant les X dernières visites.
  * **Boucle de correction :** Sous chaque photo, un menu déroulant permettant de corriger l'ID du chat assigné par l'IA ou de créer un nouveau profil. Cette action doit mettre à jour le vecteur de référence dans SQLite pour améliorer la précision future.

### E. Intégration Firebase (Storage + FCM)
Si la détection passe le filtre du cooldown, le script prépare la notification :
1. **Storage :** Uploader l'image recadrée sur Firebase Cloud Storage via `firebase-admin`. Récupérer l'URL publique générée.
2. **Push (FCM) :** Envoyer un payload JSON via Firebase Cloud Messaging aux tokens de nos appareils Android. Le payload contient : Titre ("Nouveau visiteur !"), Corps ("Félix est là !"), et l'URL publique de l'image.
3. **Nettoyage Cloud :** Intégrer une fonction qui supprime automatiquement les images de Firebase Storage de plus de 48 heures.

### F. Ménage Local
* Intégrer une fonction qui nettoie le dossier de sauvegarde local des images vieilles de plus de 30 jours.

---

## 2. L'APPLICATION MOBILE (Kotlin / Android Studio)
*(À coder après le backend)*
* Application native 100% sur mesure, sans UI complexe.
* Intégration du SDK Firebase.
* Implémentation d'un `FirebaseMessagingService` fonctionnant en arrière-plan (capable de réveiller l'appareil via réseau cellulaire).
* À la réception du message FCM, l'app télécharge l'image depuis l'URL Firebase.
* Génération d'une notification système Android locale utilisant `NotificationCompat.Builder` avec le style `BigPictureStyle` pour afficher la photo directement sous le texte.

---

## RÈGLES DE DÉVELOPPEMENT STRICTES
1. **Une étape à la fois :** Ne jamais générer de code sans instruction explicite et avancer pas à pas.
2. **Indépendance du code :** Tout le code du programme doit être autonome. Aucune dépendance avec des fichiers externes ailleurs sur le PC.
3. **Documentation continue :** Tenir absolument à jour les fichiers `.md`, incluant un fichier `changelog.md` qui sera méticuleusement mis à jour à chaque révision de code.
4. **Séparation du projet :** Le projet sera géré séparément dans deux sous-dossiers : `Windows/` (Backend Python) et `Android/` (App mobile).
5. **Préparation GitHub :** Chaque programme devra inclure son fichier `.gitignore` spécifique afin de garantir un futur commit propre vers GitHub de la v1.0.

---

## MISSION ACTUELLE
Phase d'analyse et de discussion en cours. Ne générer aucun code avant d'en recevoir l'instruction explicite de l'utilisateur.