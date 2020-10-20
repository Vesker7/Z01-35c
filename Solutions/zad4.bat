@echo off
if %1 LSS 1 (exit /b)
if %1 EQU 1 (echo 1 & exit /b)

setlocal enabledelayedexpansion

set /a prev = 1
set /a curr = 1
echo %prev%


for /l %%i in (1,1,%1) do (
	set /a next = !prev! + !curr!
	set /a prev = !curr!
	echo !curr!
	set /a curr = !next!
)

endlocal
