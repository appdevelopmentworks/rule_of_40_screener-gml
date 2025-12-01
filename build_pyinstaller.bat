@echo off
chcp 932
REM ============================================
REM Rule of 40 Screener - PyInstaller ビルドスクリプト
REM ============================================

echo ========================================
echo Rule of 40 Screener ビルド開始
echo ビルドツール: PyInstaller
echo ========================================
echo.

REM 仮想環境の確認
if exist venv\Scripts\activate.bat (
    echo 仮想環境を有効化中...
    call venv\Scripts\activate.bat
) else (
    echo 警告: 仮想環境が見つかりません
    echo 続行しますか？ (Y/N)
    set /p CONTINUE=
    if /i not "%CONTINUE%"=="Y" exit /b
)

REM 古いビルドファイルをクリーンアップ
echo.
echo 古いビルドファイルをクリーンアップ中...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo クリーンアップ完了

REM PyInstallerのインストール確認
echo.
echo PyInstallerのバージョン確認...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstallerがインストールされていません
    echo インストール中...
    pip install pyinstaller
)

REM ビルド実行
echo.
echo ========================================
echo ビルドを実行中...
echo ========================================
pyinstaller Rule40Screener.spec --clean --noconfirm

REM ビルド結果の確認
if exist dist\Rule40Screener.exe (
    echo.
    echo ========================================
    echo ビルド成功！
    echo ========================================
    echo.
    echo 実行ファイル: dist\Rule40Screener.exe
    echo.
    echo 実行ファイルのサイズ:
    dir dist\Rule40Screener.exe | find "Rule40Screener.exe"
    echo.
    echo エクスプローラーで開きますか？ (Y/N)
    set /p OPEN=
    if /i "%OPEN%"=="Y" explorer dist
) else (
    echo.
    echo ========================================
    echo ビルド失敗
    echo ========================================
    echo.
    echo エラーログを確認してください
    pause
    exit /b 1
)

echo.
echo ビルド処理完了
pause
