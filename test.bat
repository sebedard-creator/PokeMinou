@echo off
echo '%%main.py%%'
wmic process where "CommandLine like '%%main.py%%'" get ProcessId,CommandLine
