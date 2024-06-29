@echo off
setlocal enabledelayedexpansion

:: Configuration
set REPO_URL=https://github.com/ssemakulaumar/super-AI
set MAIN_PY_PATH=main.py
set MONITOR_PY_PATH=monitor.py
set CONFIG_FILE=config.json
set DEST_DIR=%~dp0AI_Script_Files

:: Check if a command exists
:check_command
set cmd=%1
where %cmd% > nul 2>&1
if not %errorlevel%==0 (
    echo %cmd% is not installed or not found in PATH.
    exit /b 1
)
goto :eof

:: Install Python packages using pip
:install_package
set package=%1
pip install %package%
if not %errorlevel%==0 (
    echo Failed to install %package%.
    exit /b 1
)
goto :eof

:: Install Git if missing
:install_git
echo Installing Git...
powershell -Command "Start-Process -Wait -Verb RunAs powershell \"Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/git-for-windows/git/master/installer/install.ps1'))\""
if not %errorlevel%==0 (
    echo Failed to install Git.
    exit /b 1
)
goto :eof

:: Install Python if missing
:install_python
echo Installing Python...
powershell -Command "Start-Process -Wait -Verb RunAs powershell \"Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe' -OutFile 'python_installer.exe'; Start-Process -Wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1\""
if not %errorlevel%==0 (
    echo Failed to install Python.
    exit /b 1
)
goto :eof

:: Check prerequisites and install if missing
:check_prerequisites
where git > nul 2>&1
if %errorlevel% neq 0 call :install_git

where python > nul 2>&1
if %errorlevel% neq 0 call :install_python

where pip > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    powershell -Command "Start-Process -Wait -Verb RunAs python \"-m ensurepip --upgrade\""
    if not %errorlevel%==0 (
        echo Failed to install pip.
        exit /b 1
    )
)

:: Install Python packages
pip show watchdog > nul 2>&1
if %errorlevel% neq 0 call :install_package watchdog

pip show psutil > nul 2>&1
if %errorlevel% neq 0 call :install_package psutil

pip show gitpython > nul 2>&1
if %errorlevel% neq 0 call :install_package gitpython
goto :eof

:: Check for updates
:check_for_updates
echo Checking for updates...
git fetch
for /f "delims=" %%i in ('git rev-parse HEAD') do set local_commit=%%i
for /f "delims=" %%i in ('git rev-parse origin/main') do set remote_commit=%%i
if not "!local_commit!"=="!remote_commit!" (
    echo Update found.
    set updates_found=true
) else (
    echo No updates found.
    set updates_found=false
)
goto :eof

:: Update script
:update_script
echo Updating script...
git pull origin main
if not %errorlevel%==0 (
    echo Failed to update script.
    exit /b 1
)
goto :eof

:: Restart script
:restart_script
echo Restarting script...
start "" "%~dp0%~nx0"
exit /b
goto :eof

:: Create directory and copy files
:create_directory_and_copy_files
if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%"
    if %errorlevel% neq 0 (
        echo Failed to create directory %DEST_DIR%.
        exit /b 1
    )
)

xcopy /y "%~dp0*.py" "%DEST_DIR%"
if %errorlevel% neq 0 (
    echo Failed to copy files to %DEST_DIR%.
    exit /b 1
)
goto :eof

:: Main script
call :check_prerequisites

:: Create directory and copy AI script files
call :create_directory_and_copy_files

:: Check for updates and apply them if found
call :check_for_updates
if "%updates_found%"=="true" (
    call :update_script
    call :restart_script
)

:: Run the Python monitoring script
echo Running monitoring script...
start /min python %DEST_DIR%\%MONITOR_PY_PATH%

echo Monitoring started.
pause
endlocal
exit /b
