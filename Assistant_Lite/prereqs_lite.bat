@echo off
setlocal enabledelayedexpansion

echo ===================================
echo Age of Empires IV Strategy Helper Setup
echo ===================================
echo.


net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges for global hotkeys.
    echo Please right-click this file and select "Run as administrator".
    echo Press any key to exit...
    pause >nul
    exit /b 1
)


python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    

    mkdir temp_downloads 2>nul
    cd temp_downloads
    

    echo Downloading Python installer...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    
    if not exist python_installer.exe (
        echo Failed to download Python installer. Please check your internet connection or install Python manually from https://www.python.org/downloads/
        exit /b 1
    )
    
    echo Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1
    
    timeout /t 10 /nobreak >nul
    
    cd ..
    rmdir /s /q temp_downloads
    
    python --version >nul 2>&1
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

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    if not exist get-pip.py (
        echo Failed to download get-pip.py. Please check your internet connection.
        exit /b 1
    )
    python get-pip.py
    del get-pip.py
)

echo Installing requests library...
python -m pip install requests
if %errorlevel% neq 0 (
    echo Failed to install the requests library.
    exit /b 1
)

echo Installing keyboard library...
python -m pip install keyboard
if %errorlevel% neq 0 (
    echo Failed to install the keyboard library. Hotkeys may not work without it.
    exit /b 1
)

if not exist matchup_strategies.csv (
    echo Warning: matchup_strategies.csv not found in the current directory.
    echo The application requires this file for strategies. Please ensure it’s present.
)

echo.
echo Setup complete! You can now run the Age of Empires IV Strategy Helper.
echo.
echo Note: Run this script or the Python script as administrator for hotkeys (Insert/F10) to work in-game.
echo To run manually, use: python Assistant_lite.py
echo.
echo Press any key to launch the application...
pause >nul

python Assistant_lite.py

endlocal
