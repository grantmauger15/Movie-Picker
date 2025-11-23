@echo off
echo Adding current directory to global PATH...

set "CURRENT_DIR=%cd%"

:: Check if already in PATH
echo %PATH% | find "%CURRENT_DIR%" >nul
if %errorlevel%==0 (
    echo Already in PATH.
    goto :done
)

:: Append to PATH globally
setx PATH "%PATH%;%CURRENT_DIR%"

echo Added: %CURRENT_DIR%
echo (Restart CMD or your PC for changes to apply.)

:done
pause
