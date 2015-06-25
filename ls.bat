@echo off

python %~dp0\ls_main.py %*
exit /B %ERRORLEVEL%

