@echo off
chcp 65001 >nul
REM ============================================
REM Rule of 40 Screener - Nuitka Build Script
REM ============================================

echo ========================================
echo Rule of 40 Screener Build
echo Build Tool: Nuitka
echo ========================================
echo.

REM Check for virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Continue anyway? (Y/N)
    set /p CONTINUE=
    if /i not "%CONTINUE%"=="Y" exit /b
)

REM Clean up old build files
echo.
echo Cleaning up old build files...
if exist Rule40Screener.dist rmdir /s /q Rule40Screener.dist
if exist Rule40Screener.build rmdir /s /q Rule40Screener.build
if exist "Rule40Screener.exe" del /q "Rule40Screener.exe"
echo Cleanup complete

REM Check Nuitka installation
echo.
echo Checking Nuitka version...
pip show nuitka >nul 2>&1
if errorlevel 1 (
    echo Nuitka not installed
    echo Installing Nuitka...
    pip install nuitka
)

REM Check C/C++ compiler
echo.
echo Checking C/C++ compiler...
echo Please ensure MinGW64 is installed
echo.

REM Execute build
echo.
echo ========================================
echo Building executable...
echo NOTE: First build may take 30-60 minutes
echo ========================================
echo.

nuitka --standalone ^
    --onefile ^
    --windows-disable-console ^
    --enable-plugin=pyside6 ^
    --include-package=src.core ^
    --include-package=src.ui ^
    --include-package=yfinance ^
    --include-package=pandas ^
    --include-package=numpy ^
    --include-package=requests ^
    --include-package=bs4 ^
    --include-package=cloudscraper ^
    --include-package=openpyxl ^
    --include-data-file="src\config.yaml=src\config.yaml" ^
    --include-data-file="appimg.ico=appimg.ico" ^
    --windows-icon-from-ico="appimg.ico" ^
    --output-filename="Rule40Screener.exe" ^
    --company-name="Rule40 Screener" ^
    --product-name="Rule of 40 Screener" ^
    --file-version=1.0.0 ^
    --product-version=1.0.0 ^
    --file-description="Rule of 40 Stock Screener" ^
    --copyright="Copyright 2025" ^
    --show-progress ^
    --show-memory ^
    "src\app.py"

REM Check build result
if exist "Rule40Screener.exe" (
    echo.
    echo ========================================
    echo Build Successful!
    echo ========================================
    echo.
    echo Executable: Rule40Screener.exe
    echo.
    echo File size:
    dir "Rule40Screener.exe" | find "Rule40Screener.exe"
    echo.
    echo NOTE: First run may take some time
    echo.
    echo Open in Explorer? (Y/N)
    set /p OPEN=
    if /i "%OPEN%"=="Y" explorer "."
) else (
    echo.
    echo ========================================
    echo Build Failed
    echo ========================================
    echo.
    echo Please check the error log
    echo.
    echo Common issues:
    echo - MinGW64 not installed
    echo - Missing dependencies
    echo - Insufficient memory
    pause
    exit /b 1
)

echo.
echo Build process complete
pause
