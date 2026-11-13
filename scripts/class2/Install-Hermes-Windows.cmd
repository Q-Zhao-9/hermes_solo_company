@echo off
setlocal
title AI Solo Company Class 2 - Hermes Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Hermes-Windows.ps1"
if errorlevel 1 (
  echo.
  echo Installation stopped with an error. Please take a screenshot for your teacher.
  pause
)
endlocal
