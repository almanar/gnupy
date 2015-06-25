@echo off

python %~dp0\ls_main.py -lF %*
exit /B %ERRORLEVEL%

