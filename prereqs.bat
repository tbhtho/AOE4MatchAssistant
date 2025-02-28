@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Age of Empires IV Strategy Helper Setup
echo ===================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    
    REM Create temporary directory for downloads
    mkdir temp_downloads 2> nul
    cd temp_downloads
    
    REM Download Python installer
    echo Downloading Python installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    
    if not exist python_installer.exe (
        echo Failed to download Python installer. Please check your internet connection.
        exit /b 1
    )
    
    echo Installing Python...
    REM Install Python with pip and add Python to PATH
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1
    
    REM Wait for installation to complete
    timeout /t 10 /nobreak > nul
    
    cd ..
    rmdir /s /q temp_downloads
    
    REM Verify Python installation
    python --version > nul 2>&1
    if %errorlevel% neq 0 (
        echo Python installation failed. Please install Python manually from https://www.python.org/downloads/
        exit /b 1
    ) else (
        echo Python installed successfully.
    )
) else (
    echo Python is already installed.
)

echo.
echo Installing required libraries...

REM Check if pip is installed
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    del get-pip.py
)

REM Install required libraries
python -m pip install requests
if %errorlevel% neq 0 (
    echo Failed to install the requests library.
    exit /b 1
)

echo.
echo Setup complete! You can now run the Age of Empires IV Strategy Helper.
echo.
echo To run the application, use: python aoe4strat.py
echo.
echo Press any key to run the application...
pause > nul

python aoe4strat.py

endlocal