@echo off
set "DIR=%~dp0"
echo Adding %DIR% to PATH...
setx PATH "%PATH%;%DIR%"
echo Done.
