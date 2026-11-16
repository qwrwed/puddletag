@echo off
rem Starts this patched puddletag with its settings, actions and theme.json kept in .\config\puddletag.
set "HERE=%~dp0"
set "XDG_CONFIG_HOME=%HERE%config"
set "XDG_DATA_HOME=%HERE%config"
start "" "%HERE%.venv\Scripts\pythonw.exe" "%HERE%puddletag" %*
