@echo off
setlocal
title Building Golf Sim Launcher
where py >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Install Python 3 for Windows.
  pause
  exit /b 1
)
py -m pip install --upgrade pyinstaller pillow
if errorlevel 1 (
  echo Could not install required packages.
  pause
  exit /b 1
)
py -m PyInstaller --noconfirm --clean --onefile --windowed --add-data "background.png;." --name GolfSimLauncher GolfSimLauncher.py
if errorlevel 1 (
  echo BUILD FAILED.
  pause
  exit /b 1
)
echo.
echo BUILD COMPLETE:
echo dist\GolfSimLauncher.exe
pause
