@echo off
echo ==============================================
echo        Lancement de PokeMinou (Bridge + AI)
echo ==============================================
echo.

echo [1/2] Lancement du pont Eufy en arriere-plan...
set USERNAME=sebedard666@hotmail.com
set PASSWORD=PokeMinou666$$$
cd /d "%~dp0Windows\eufy-bridge"
start /B "" "node_modules\.bin\eufy-security-server.cmd" > bridge_logs.txt 2>&1

:: Attendre 5 secondes pour que le port 3000 s'ouvre bien (ping fonctionne mieux en mode silencieux)
ping 127.0.0.1 -n 6 > nul

echo.
echo [2/2] Lancement du backend AI PokeMinou...
cd /d "%~dp0Windows"
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo L'interface d'administration Gradio sera disponible sur :
echo http://10.0.0.30:8095
echo.
python main.py
exit /b
