@echo off
setlocal enabledelayedexpansion
title Java Institute - Class Auto Joiner Pro

cd /d "%~dp0"

echo ================================================================
echo          Java Institute - Class Auto Joiner Pro Setup
echo ================================================================
echo.

:: ---------------------------------------------------------
:: 1. Check for Python Installation
:: ---------------------------------------------------------
set "PYTHON_CMD="

:: Check system PATH python
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

:: Check py launcher
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

:: Check common installation directories
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :PYTHON_FOUND
    )
)
for /d %%D in ("%ProgramFiles%\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :PYTHON_FOUND
    )
)

:: If Python is not found, attempt automatic installation
echo [!] Python was not found on your computer.
echo [*] Downloading and installing Python automatically... Please wait.
echo.

set "INSTALLER_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "INSTALLER_PATH=%TEMP%\python_installer.exe"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('%INSTALLER_URL%', '%INSTALLER_PATH%')" >nul 2>&1

if exist "%INSTALLER_PATH%" (
    echo [*] Installing Python (this may take 1-2 minutes)...
    start /wait "" "%INSTALLER_PATH%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
    del /f /q "%INSTALLER_PATH%" >nul 2>&1
    
    :: Refresh Environment Variables from Registry
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
    for /f "tokens=2*" %%A in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
    
    python --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
        echo [+] Python installed successfully!
        echo.
        goto :PYTHON_FOUND
    )
    
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%D\python.exe" (
            set "PYTHON_CMD=%%D\python.exe"
            goto :PYTHON_FOUND
        )
    )
)

echo.
echo [X] Could not install Python automatically.
echo Please install Python manually from https://www.python.org/downloads/
echo (Make sure to check "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [+] Python detected.

:: ---------------------------------------------------------
:: 2. Setup / Check Virtual Environment (.venv)
:: ---------------------------------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment (.venv)...
    "%PYTHON_CMD%" -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Could not create virtual environment. Using system Python directly.
        set "PY_EXEC=%PYTHON_CMD%"
    ) else (
        set "PY_EXEC=.venv\Scripts\python.exe"
    )
) else (
    set "PY_EXEC=.venv\Scripts\python.exe"
)

:: ---------------------------------------------------------
:: 3. Check and Install Required Python Libraries
:: ---------------------------------------------------------
echo [*] Checking and updating required Python libraries...
"%PY_EXEC%" -m pip install --disable-pip-version-check --no-warn-script-location -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Failed to install required libraries. Retrying with basic dependencies...
    "%PY_EXEC%" -m pip install customtkinter selenium webdriver-manager
)

:: ---------------------------------------------------------
:: 4. Check for Google Chrome (Required for Automation)
:: ---------------------------------------------------------
set "CHROME_FOUND=0"
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1 && set "CHROME_FOUND=1"
reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1 && set "CHROME_FOUND=1"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=1"
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=1"
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set "CHROME_FOUND=1"

if "%CHROME_FOUND%"=="0" (
    echo.
    echo [!] Warning: Google Chrome was not detected on this system.
    echo     Please make sure Google Chrome is installed so that class auto-joining works properly.
    echo.
)

:: ---------------------------------------------------------
:: 5. Launch the Application
:: ---------------------------------------------------------
echo.
echo [+] Starting Java Institute Class Auto Joiner Pro...
echo ================================================================
echo.

"%PY_EXEC%" app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ================================================================
    echo [X] An error occurred while running the application.
    echo ================================================================
    echo.
    pause
)
