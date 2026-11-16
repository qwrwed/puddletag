@echo off
rem Starts this patched puddletag with its settings and theme.json kept in .\home.
set "HERE=%~dp0"
set "HOME=%HERE%home"
set "XDG_CONFIG_HOME=%HERE%home\.config"
set "XDG_DATA_HOME=%HERE%home\.local\share"
start "" "%HERE%.venv\Scripts\pythonw.exe" "%HERE%puddletag" %*
