@echo off
REM Double-click this file to play The Job Interview Disaster on Windows.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py game.py) else (python game.py)
if errorlevel 1 pause
