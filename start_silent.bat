@echo off
cd /d "%~dp0"
echo Lancement silencieux en cours... > Windows\startup_logs.txt
call start.bat >> Windows\startup_logs.txt 2>&1
