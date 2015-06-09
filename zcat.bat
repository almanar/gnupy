@echo off

python %~dp0\gzip_main.py -c -d %*
exit /B %ERRORLEVEL%

