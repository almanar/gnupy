@echo off

python %~dp0\unix2dos_main.py unix2dos %*
exit /B %ERRORLEVEL%

