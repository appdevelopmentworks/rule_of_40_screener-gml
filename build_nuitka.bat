@echo off
chcp 932
REM ============================================
REM Rule of 40 Screener - Nuitka ビルドスクリプト
REM ============================================

echo ========================================
echo Rule of 40 Screener ビルド開始
echo ビルドツール: Nuitka
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
if exist Rule40Screener.dist rmdir /s /q Rule40Screener.dist
if exist Rule40Screener.build rmdir /s /q Rule40Screener.build
if exist Rule40Screener.exe del /q Rule40Screener.exe
echo クリーンアップ完了

REM Nuitkaのインストール確認
echo.
echo Nuitkaのバージョン確認...
pip show nuitka >nul 2>&1
if errorlevel 1 (
    echo Nuitkaがインストールされていません
    echo インストール中...
    pip install nuitka
)

REM C/C++コンパイラの確認
echo.
echo C/C++コンパイラの確認...
echo MinGW64がインストールされていることを確認してください
echo.

REM ビルド実行
echo.
echo ========================================
echo ビルドを実行中...
echo ※ 初回ビルドは時間がかかります（30分〜1時間）
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
    --include-data-file=src\config.yaml=src\config.yaml ^
    --include-data-file=appimg.ico=appimg.ico ^
    --windows-icon-from-ico=appimg.ico ^
    --output-filename=Rule40Screener.exe ^
    --company-name="Rule40 Screener" ^
    --product-name="Rule of 40 Screener" ^
    --file-version=1.0.0 ^
    --product-version=1.0.0 ^
    --file-description="Rule of 40 Stock Screener" ^
    --copyright="Copyright 2025" ^
    --show-progress ^
    --show-memory ^
    src\app.py

REM ビルド結果の確認
if exist "Rule40Screener.exe" (
    echo.
    echo ========================================
    echo ビルド成功！
    echo ========================================
    echo.
    echo 実行ファイル: Rule40Screener.exe
    echo.
    echo 実行ファイルのサイズ:
    dir "Rule40Screener.exe" | find "Rule40Screener.exe"
    echo.
    echo 注意: 初回実行時は少し時間がかかる場合があります
    echo.
    echo エクスプローラーで開きますか？ (Y/N)
    set /p OPEN=
    if /i "%OPEN%"=="Y" explorer "."
) else (
    echo.
    echo ========================================
    echo ビルド失敗
    echo ========================================
    echo.
    echo エラーログを確認してください
    echo.
    echo よくあるエラー:
    echo - MinGW64がインストールされていない
    echo - 依存パッケージが不足している
    echo - メモリ不足
    pause
    exit /b 1
)

echo.
echo ビルド処理完了
pause
