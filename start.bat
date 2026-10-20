@echo off
cd /d "%~dp0"
title StudentAI
where python >nul 2>nul
if %errorlevel%==0 (
  python server.py
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py server.py
  ) else (
    echo Python is not installed.
    echo Install it from https://www.python.org/downloads/ and tick "Add Python to PATH", then double-click this file again.
  )
)
pause
