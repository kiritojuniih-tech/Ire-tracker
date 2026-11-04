@echo off
cd /d "%~dp0"
echo IRE TRACKER - CONEXAO RIOT
set /p RIOT_API_KEY=Cole sua Riot API Key aqui (nao compartilhe): 
if "%RIOT_API_KEY%"=="" (echo Chave vazia. & pause & exit /b 1)
start "" http://localhost:8765
py -3 server.py
if errorlevel 1 python server.py
pause
