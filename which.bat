@echo off

python %~dp0\which_main.py %*

exit /B %ERRORLEVEL%
