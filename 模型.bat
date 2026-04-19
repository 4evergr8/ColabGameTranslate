@echo off
chcp 65001
setlocal
cd /d %~dp0
start "" /b llama\llama-server.exe  -m llama\gemma-4-E4B-it-UD-Q8_K_XL.gguf  --context-shift  --reasoning off
pause
endlocal