@echo off

if exist %1 (dir %1\*%2) else (echo "Directory doesnt exist!")