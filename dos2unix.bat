@echo off

python %~dp0\unix2dos_main.py dos2unix %*
exit /B %ERRORLEVEL%

