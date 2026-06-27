@echo off
title PokeMinou (Server)
echo ==============================================
echo        Lancement de PokeMinou (RTSP + AI)
echo ==============================================
echo.

cd /d "%~dp0Windows"
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo L'interface d'administration Gradio sera disponible sur :
echo http://10.0.0.30:8095
echo.

python main.py
exit /b
