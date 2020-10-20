@echo off

if exist %1 (xcopy %1 %2 /t /e) else (echo "Directory doesn't exist")
