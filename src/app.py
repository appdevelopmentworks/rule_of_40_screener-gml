"""
Rule of 40 Screener - メインアプリケーション
"""

import logging
import os
import sys
from pathlib import Path

# プロジェクトルートを Python パスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication

# 設定管理
from core.data.config_loader import ConfigManager
from core.domain.models import ConfigError

# UI コンポーネント
from ui.main_window import MainWindow


def setup_logging(config_manager: ConfigManager):
    """ログ設定"""
    log_level = config_manager.get("logging.level", "INFO")
    log_dir = config_manager.get("logging.log_dir", "app_data/logs")

    # ログディレクトリ作成
    os.makedirs(log_dir, exist_ok=True)

    # ログファイル名
    from datetime import datetime

    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    # ログ設定
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            (
                logging.StreamHandler()
                if config_manager.get("logging.console_enabled", True)
                else logging.NullHandler()
            ),
        ],
    )


def setup_translation(app: QApplication, config_manager: ConfigManager):
    """翻訳設定"""
    # TODO: Implement translation loading when translation files are available
    # For now, skip translation to avoid startup errors
    pass


def load_theme(app: QApplication, config_manager: ConfigManager):
    """テーマ設定"""
    theme = config_manager.get("ui.theme", "auto")

    if theme == "dark":
        # ダークテーマ適用
        app.setStyle("Fusion")
        # TODO: ダークテーマスタイルシート適用
        pass
    elif theme == "light":
        # ライトテーマ適用
        app.setStyle("WindowsVista")
        # TODO: ライトテーマスタイルシート適用
        pass
    else:  # auto
        # OS テーマに追従
        pass


def main():
    """メインエントリーポイント"""
    try:
        # QApplication 作成
        app = QApplication(sys.argv)
        app.setApplicationName("Rule of 40 Screener")
        app.setApplicationVersion("0.1.0")
        app.setOrganizationName("Rule of 40 Screener Team")

        # 設定マネージャ初期化
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        config_manager = ConfigManager(config_path)

        # ログ設定
        setup_logging(config_manager)
        logger = logging.getLogger(__name__)
        logger.info("Starting Rule of 40 Screener")

        # 翻訳設定
        setup_translation(app, config_manager)

        # テーマ設定
        load_theme(app, config_manager)

        # アイコン設定
        # TODO: アイコンファイル作成後に設定
        # app.setWindowIcon(QIcon(':/icons/app_icon.png'))

        # メインウィンドウ作成
        main_window = MainWindow(config_manager)
        main_window.show()

        logger.info("Application started successfully")

        # イベントループ開始
        return app.exec()

    except ConfigError as e:
        # 設定エラー
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox()
        msg.setWindowTitle("設定エラー")
        msg.setText(f"設定ファイルの読み込みに失敗しました:\n{e}")
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        return 1

    except Exception as e:
        # 予期せぬエラー
        import traceback

        from PySide6.QtWidgets import QMessageBox

        error_msg = f"予期せぬエラーが発生しました:\n{e}\n\n{traceback.format_exc()}"

        # ログに出力
        logging.error(error_msg)

        # ダイアログ表示
        msg = QMessageBox()
        msg.setWindowTitle("エラー")
        msg.setText("アプリケーションの起動に失敗しました。")
        msg.setDetailedText(error_msg)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()

        return 1


if __name__ == "__main__":
    sys.exit(main())
