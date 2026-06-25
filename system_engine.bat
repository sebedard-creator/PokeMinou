@echo off
echo ==============================================
echo        Lancement de PokeMinou (RTSP + AI)
echo ==============================================
echo.

if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do set "%%A=%%B"
) else (
    echo [ATTENTION] Fichier .env introuvable a la racine.
)

echo.
echo Lancement du backend AI PokeMinou...
cd /d "%~dp0Windows"
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo L'interface d'administration Gradio sera disponible sur :
echo http://10.0.0.30:8095
echo.
python main.py
exit /b

