@echo off
cd /d "D:\WebApp Pneus\backend"
start /min cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000"
exit