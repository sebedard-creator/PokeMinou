@echo off
title Arret PokeMinou
echo ===================================================
echo   Fermeture du serveur d'Intelligence Artificielle
echo ===================================================
echo.
echo Arret des processus Python en cours...
wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" call terminate >nul 2>&1

echo.
echo Arret de ffmpeg (Capture RTSP)...
wmic process where "name='ffmpeg.exe'" call terminate >nul 2>&1

echo.
echo Serveurs arretes avec succes !
exit /b
