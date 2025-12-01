"""
PyInstallerビルドスクリプト
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build():
    """ビルド成果物をクリーン"""
    print("Cleaning previous build artifacts...")

    dirs_to_remove = ["build", "dist"]
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    spec_files = ["*.spec"]
    for spec_pattern in spec_files:
        for spec_file in Path(".").glob(spec_pattern):
            if spec_file.name != "Rule40Screener.spec":
                os.remove(spec_file)
                print(f"  Removed {spec_file}")


def build_executable():
    """実行ファイルをビルド"""
    print("\nBuilding executable with PyInstaller...")

    # PyInstallerコマンド実行
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "Rule40Screener.spec",
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

    print("Build successful!")
    return True


def verify_build():
    """ビルド結果を検証"""
    print("\nVerifying build output...")

    exe_path = Path("dist/Rule40Screener.exe")
    if not exe_path.exists():
        print(f"ERROR: Executable not found at {exe_path}")
        return False

    print(f"  Found executable: {exe_path}")
    print(f"  Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")

    return True


def main():
    """メイン処理"""
    print("=" * 60)
    print("Rule of 40 Screener - Build Script")
    print("=" * 60)

    # クリーン（オプション）
    if "--clean" in sys.argv:
        clean_build()

    # ビルド実行
    if not build_executable():
        sys.exit(1)

    # 検証
    if not verify_build():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("Executable location: dist/Rule40Screener.exe")
    print("=" * 60)


if __name__ == "__main__":
    main()
