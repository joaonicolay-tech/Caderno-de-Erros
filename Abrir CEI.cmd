@echo off
cd /d "%~dp0"
echo Caderno de Erros Inteligente - V1.0 Local
echo Depois da inicializacao, abra http://127.0.0.1:8000/ no Chrome.
echo Mantenha esta janela aberta durante o uso. Para parar, pressione Ctrl+C.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-local.ps1" -Profile production_local -Port 8000
if errorlevel 1 pause
