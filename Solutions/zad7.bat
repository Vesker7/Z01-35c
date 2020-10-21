@echo off

setlocal enabledelayedexpansion

set /a multiplier=1
set /a result=1

for /l %%i in (1,1,%1) do (
	set /a result = !result! * !multiplier!
	set /a multiplier += 1
)

echo !result!

endlocal
