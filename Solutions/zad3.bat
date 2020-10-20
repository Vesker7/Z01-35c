@echo off

verify >nul
date %DATE% 2>nul
if %errorlevel% NEQ 0 echo "You dont have Administrator rights!"