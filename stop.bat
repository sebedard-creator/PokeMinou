@echo off
title Arret PokeMinou
echo ===================================================
echo   Fermeture du serveur d'Intelligence Artificielle
echo ===================================================
echo.
echo Arret des processus Python en cours...
wmic process where "CommandLine like '%%python main.py%%'" call terminate

echo.
echo Arret du pont Eufy (Node.js)...
wmic process where "CommandLine like '%%eufy-security-ws%%'" call terminate

echo.
echo Arret des scripts de lancement silencieux...
wmic process where "CommandLine like '%%start_silent.bat%%'" call terminate >nul 2>&1
wmic process where "CommandLine like '%%system_engine.bat%%'" call terminate >nul 2>&1

echo.
echo Serveurs arretes avec succes !
exit /b
