# 🐾 PokeMinou - Feline Facial Recognition & Security System

Welcome to **PokeMinou**, a complete, AI-powered smart home ecosystem designed to identify specific cats visiting your property and send rich push notifications to your Android device in real-time.

## 🌟 Overview

The PokeMinou ecosystem is divided into two distinct but deeply integrated programs:
1. **The AI Backend (Windows/Server)**: The brain of the operation. It interfaces with your Eufy security cameras, processes video streams, runs artificial intelligence models to identify cats, and handles database management.
2. **The Android Companion App**: The visual client. It runs silently in the background of your phone and receives instant, rich push notifications with photos whenever a feline visitor is recognized.

---

## 🖥️ Program 1: The AI Backend (Windows)

Located in the `Windows/` folder, this Python-based backend acts as a highly optimized, local processing server. 

### Key Features:
- **Eufy Camera Integration (`eufy-security-ws`)**: Hooks into the Eufy cloud using a WebSocket bridge. It listens instantly to "Motion Detected" events across all your Eufy cameras.
- **P2P Video Streaming**: When motion is detected, it connects directly to the specific Eufy camera that triggered the alert, recording a 5-second raw `.h264` video clip.
- **AI Object Detection (YOLOv8)**: Analyzes the video frames to detect the presence of a cat and crops the image perfectly around the cat's face/body.
- **AI Re-Identification (ResNet50)**: Extracts a 2048-dimensional mathematical vector from the cropped image and compares it against known cats in the local SQLite database using Cosine Similarity (default threshold: 80%).
- **Smart Notification Engine**:
  - Automatically creates a new profile if the cat is unknown.
  - Features an anti-spam "Cooldown" system (default 2 minutes, dynamically adjustable) to prevent notification flooding if a cat lingers in front of the camera.
  - Automatically ignores nighttime detections using a generic `Chat_Nuit_Mystere` profile (since infrared images break color-based facial recognition).
- **Gradio Admin Web UI**: Accessible locally at `http://127.0.0.1:8095`. Allows you to:
  - View the gallery of recent cat visits.
  - Correct the AI if it makes a mistake (teach the AI a new cat's face or correct a false positive).
  - Adjust the YOLO confidence threshold and notification cooldown slider on the fly.
- **Cloud Synchronization**: Uploads the cropped cat picture to Firebase Storage and sends a Cloud Messaging (FCM) push notification containing a hidden `data payload` (Cat Name and Image URL).
- **Automated Nightly Cleaner**: Runs at 3:00 AM every day to delete local images older than 30 days and Firebase images older than 48 hours, ensuring zero disk bloat.

---

## 📱 Program 2: The Android App

Located in the `Android/` folder, this native Android application is built with modern tools (Kotlin, Jetpack Compose, and Gradle/Groovy). 

### Key Features:
- **Firebase Cloud Messaging (FCM)**: Subscribes to the global `all` topic to receive instant push alerts from the backend.
- **Background Execution**: Works seamlessly even when the app is swiped away or closed.
- **Interactive Data Payload**: When a notification is tapped, the Android OS passes the invisible `image_url` and `cat_name` to the app's `MainActivity`.
- **Dynamic Compose UI**: 
  - Defaults to a sleek "Waiting Screen".
  - Instantly updates to a "Cat Detected Screen" when a notification is clicked.
  - Uses **Coil** to asynchronously download and display the high-resolution photo of the visiting cat right on your phone screen.
- **Modern & Premium Design**: Features a dark mode, neo-morphic aesthetic using Material Design 3 guidelines.

---

## 🚀 Getting Started

### Backend Setup:
1. Ensure the Eufy Security WebSocket bridge is running.
2. Configure your `core/config.py` with your RTSP/Eufy URLs and Firebase Storage bucket.
3. Place your `serviceAccountKey.json` from Firebase in the root of the Windows folder.
4. Run `start.bat` (or use `StartPokeMinou.vbs` to run it invisibly on Windows Startup).

### Android Setup:
1. Place your `google-services.json` file in the `Android/app/` directory.
2. Open the `Android` folder in Android Studio.
3. Build and install the APK on your device.
4. Grant the "Post Notifications" permission when prompted.

---
*Created with ❤️ for smart homes and smarter cats.*
