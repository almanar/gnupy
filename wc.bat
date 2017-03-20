@echo off

python %~dp0\wc_main.py %*

exit /B %ERRORLEVEL%
