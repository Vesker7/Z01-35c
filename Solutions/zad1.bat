@echo off

if not exist %1 goto :notex
dir %1\*%2
goto :eof
:notex
echo "Directory doesnt exist!"
