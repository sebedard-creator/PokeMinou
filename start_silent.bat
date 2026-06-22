@echo off
cd /d "%~dp0"
echo Lancement silencieux en cours... > Windows\startup.log
call system_engine.bat >> Windows\startup.log 2>&1
