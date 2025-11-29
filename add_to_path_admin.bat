@echo off
setlocal

:: Get the directory where this BAT file is located.
:: %~dp0 returns the drive and path of the script, including a trailing backslash.
set "TargetDir=%~dp0"

:: Remove the trailing backslash for cleaner output and consistency.
if "%TargetDir:~-1%"=="\" set "TargetDir=%TargetDir:~0,-1%"

echo =========================================================
echo PATH Modifier Script
echo =========================================================
echo Target Directory: "%TargetDir%"
echo.

:: -----------------------------------------------------------
:: CHECK FOR ADMINISTRATOR PRIVILEGES
:: The SETX /M command requires elevated privileges.
:: -----------------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator.
    echo Please right-click the BAT file and select "Run as administrator".
    echo The PATH variable will NOT be modified.
    echo.
    pause
    goto :eof
)
echo Administrator privileges confirmed.

:: -----------------------------------------------------------
:: CHECK FOR DUPLICATION
:: Check if the directory already exists in the System PATH to prevent redundancy.
:: We query the registry value directly for the System PATH variable.
:: -----------------------------------------------------------
echo Checking current System PATH for existing entry...
set "PathFound="
for /f "tokens=*" %%p in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i /c:"%TargetDir%"') do (
    set "PathFound=true"
)

if defined PathFound (
    echo RESULT: The directory is ALREADY included in the System PATH.
    echo No action was necessary.
) else (
    :: -----------------------------------------------------------
    :: EXECUTE PATH MODIFICATION
    :: %PATH% is the existing system variable. We append the new directory.
    :: -----------------------------------------------------------
    echo Adding directory to the System PATH...
    
    :: Use SETX /M to permanently modify the Machine (System) PATH.
    :: NOTE: SETX limits the variable length to 1024 characters.
    setx /M PATH "%%PATH%%;%TargetDir%"
    
    echo.
    echo SUCCESS: "%TargetDir%" has been permanently added to the System PATH.
    echo 
    echo =========================================================
    echo ACTION REQUIRED:
    echo For the changes to take effect:
    echo 1. You MUST close and reopen any existing Command Prompt or PowerShell window.
    echo 2. For system-wide applications, a full system restart may be necessary.
    echo =========================================================
)

endlocal
pause