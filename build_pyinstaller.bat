@echo off
chcp 65001 >nul
REM ============================================
REM Rule of 40 Screener - PyInstaller Build Script
REM ============================================

echo ========================================
echo Rule of 40 Screener Build
echo Build Tool: PyInstaller
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
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Cleanup complete

REM Check PyInstaller installation
echo.
echo Checking PyInstaller version...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not installed
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Execute build
echo.
echo ========================================
echo Building executable...
echo ========================================
pyinstaller "Rule40Screener.spec" --clean --noconfirm

REM Check build result
if exist "dist\Rule40Screener.exe" (
    echo.
    echo ========================================
    echo Build Successful!
    echo ========================================
    echo.
    echo Executable: dist\Rule40Screener.exe
    echo.
    echo File size:
    dir "dist\Rule40Screener.exe" | find "Rule40Screener.exe"
    echo.
    echo Open in Explorer? (Y/N)
    set /p OPEN=
    if /i "%OPEN%"=="Y" explorer "dist"
) else (
    echo.
    echo ========================================
    echo Build Failed
    echo ========================================
    echo.
    echo Please check the error log
    pause
    exit /b 1
)

echo.
echo Build process complete
pause
