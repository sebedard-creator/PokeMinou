@echo off
:: Ce script doit être exécuté en tant qu'Administrateur
echo ===================================================
echo   Configuration du Pare-Feu Windows pour PokeMinou
echo ===================================================
echo.

echo Ajout de l'autorisation pour l'environnement virtuel Python...
netsh advfirewall firewall add rule name="PokeMinou Python" dir=in action=allow program="%~dp0Windows\venv\Scripts\python.exe" enable=yes
netsh advfirewall firewall add rule name="PokeMinou Python" dir=out action=allow program="%~dp0Windows\venv\Scripts\python.exe" enable=yes

echo.
echo Ajout de l'autorisation pour ffmpeg (Capture RTSP)...
:: Supposant que ffmpeg est dans le PATH de Windows, on l'autorise globalement
netsh advfirewall firewall add rule name="PokeMinou FFMPEG" dir=in action=allow program="ffmpeg.exe" enable=yes
netsh advfirewall firewall add rule name="PokeMinou FFMPEG" dir=out action=allow program="ffmpeg.exe" enable=yes

echo.
echo Configuration du pare-feu terminee !
pause
