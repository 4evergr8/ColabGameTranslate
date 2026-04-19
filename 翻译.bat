@echo off
chcp 65001
setlocal
cd /d %~dp0
.\.venv\Scripts\python.exe 3,翻译Gemma4.py
pause
endlocal