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
taskkill /F /IM node.exe /T

echo.
echo Serveurs arretes avec succes !
exit /b
