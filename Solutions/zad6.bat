@echo off
cls
echo %1
set leaf=--
call :tree %1
pause
exit /b

:tree
set _element=%1
set _element=%_element:"=%
for /f "tokens=*" %%i in ('dir "%_element%\" /a:d /b') do ( 
call :print "%%i" %leaf%
call :tree "%_element%\%%i"
set leaf=%leaf%--
)
exit /b

:print
set string=%1
set string=%string:"=%
echo  ^|%2%string%
exit /b