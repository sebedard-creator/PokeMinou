@echo off
echo ==============================================
echo        Lancement de PokeMinou (Bridge + AI)
echo ==============================================
echo.

echo [1/2] Lancement du pont Eufy en arriere-plan...
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do set "%%A=%%B"
) else (
    echo [ATTENTION] Fichier .env introuvable a la racine. Les identifiants Eufy ne sont pas configures !
)
cd /d "%~dp0Windows\eufy-bridge"
"%~dp0Windows\venv\Scripts\python.exe" sync_env.py
start /B "" run_node.bat

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
