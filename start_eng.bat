@echo off
chcp 65001 >nul
title Google SEO Analysis Tool
color 0B

echo.
echo ========================================
echo    GOOGLE SEO ANALYSIS TOOL
echo ========================================
echo.

:: Python check
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo During installation, check "Add Python to PATH" option!
    echo.
    pause
    exit /b 1
)

:: Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYVER=%%a
echo Python version: %PYVER%

:: Library check
echo.
echo Checking libraries...
echo.

set LIB_ERROR=0

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] requests - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] requests
)

python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] pandas - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] pandas
)

python -c "import halo" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] halo - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] halo
)

python -c "import termcolor" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] termcolor - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] termcolor
)

python -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] openpyxl - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] openpyxl
)

python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] python-dotenv - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] python-dotenv
)

python -c "import bs4" >nul 2>&1
if %errorlevel% neq 0 (
    echo [  ] beautifulsoup4 - NOT FOUND
    set LIB_ERROR=1
) else (
    echo [OK] beautifulsoup4
)

:: Install missing libraries
if %LIB_ERROR%==1 (
    echo.
    echo Missing libraries found, installing...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Library installation failed!
        echo.
        echo If pip command didn't work, reinstall Python
        echo and check "Add Python to PATH" option.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Libraries installed successfully!
)

echo.
echo ========================================

:: .env file check
if not exist .env (
    echo.
    echo ERROR: .env file not found!
    echo.
    echo Please copy .env.example to .env
    echo and add your API credentials.
    echo.
    echo Example:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

:: Show menu
echo.
echo  What analysis would you like to run?
echo.
echo    [1] Rank Tracker (specific keywords)
echo    [2] Automatic Competitor Analysis (enter site only)
echo    [3] Exit
echo.

set /p CHOICE="Your choice (1/2/3): "

if "%CHOICE%"=="1" goto RANK
if "%CHOICE%"=="2" goto COMPETITOR
if "%CHOICE%"=="3" goto EXIT
echo Invalid choice!
pause
goto RANK

:COMPETITOR
echo.
echo ========================================
echo    AUTOMATIC COMPETITOR ANALYSIS
echo ========================================
echo.
python rakip_analiz.py
goto DONE

:RANK
echo.
echo ========================================
echo    RANK TRACKER
echo ========================================
echo.
echo Enter information (leave blank for defaults):
echo.

set /p KEYWORD="Keyword [running shoes]: "
set /p MYSITE="Your website [https://www.adidas.com/]: "
set /p COMP1="Competitor 1 [https://www.nike.com]: "
set /p COMP2="Competitor 2 [https://www.reebok.com]: "
set /p COMP3="Competitor 3 [https://www.asics.com]: "
set /p COMP4="Competitor 4 [https://www.hoka.com]: "

echo.
echo ========================================
echo    Parameters:
echo ========================================
echo    Keyword   : %KEYWORD%
echo    My Site   : %MYSITE%
echo    Competitor 1: %COMP1%
echo    Competitor 2: %COMP2%
echo    Competitor 3: %COMP3%
echo    Competitor 4: %COMP4%
echo ========================================
echo.

set /p CONFIRM="Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

:: Build parameters
set PARAMS=

if not "%KEYWORD%"=="" set PARAMS=%PARAMS% -k "%KEYWORD%"
if not "%MYSITE%"=="" set PARAMS=%PARAMS% -s "%MYSITE%"

:: Add competitors
set COMPS=
if not "%COMP1%"=="" set COMPS=%COMP1%
if not "%COMP2%"=="" set COMPS=%COMP1% %COMP2%
if not "%COMP3%"=="" set COMPS=%COMP1% %COMP2% %COMP3%
if not "%COMP4%"=="" set COMPS=%COMP1% %COMP2% %COMP3% %COMP4%

if not "%COMPS%"=="" set PARAMS=%PARAMS% -r %COMPS%

echo.
echo Running...
echo.
python rank_tracker.py %PARAMS%
goto DONE

:EXIT
echo.
echo Goodbye!
pause
exit /b 0

:DONE
echo.

if %errorlevel% equ 0 (
    echo ========================================
    echo    Operation completed successfully!
    echo ========================================
) else (
    echo ========================================
    echo    An error occurred!
    echo ========================================
)

echo.
pause
