@echo off
title Arret PokeMinou
echo ===================================================
echo   Fermeture du serveur d'Intelligence Artificielle
echo ===================================================
echo.
echo Arret des processus Python en cours...
taskkill /F /IM python.exe /T

echo.
echo Arret du pont Eufy (Node.js)...
taskkill /F /IM node.exe /T

echo.
echo Serveurs arretes avec succes !
pause
