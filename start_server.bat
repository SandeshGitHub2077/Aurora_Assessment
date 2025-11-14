@echo off
echo Starting QA System Server...
E:\conda_envs\qa-system\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8001
pause

