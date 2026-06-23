@echo off
title Arret PokeMinou
echo ===================================================
echo   Fermeture du serveur d'Intelligence Artificielle
echo ===================================================
echo.
echo Arret des processus Python en cours...
wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" call terminate >nul 2>&1

echo.
echo Arret du pont Eufy (Node.js)...
wmic process where "name='node.exe' and CommandLine like '%%eufy-security-ws%%'" call terminate >nul 2>&1

echo.
echo Arret des scripts de lancement silencieux...
wmic process where "name='cmd.exe' and CommandLine like '%%start_silent.bat%%'" call terminate >nul 2>&1
wmic process where "name='cmd.exe' and CommandLine like '%%system_engine.bat%%'" call terminate >nul 2>&1
wmic process where "name='cmd.exe' and CommandLine like '%%run_node.bat%%'" call terminate >nul 2>&1

echo.
echo Serveurs arretes avec succes !
exit /b
