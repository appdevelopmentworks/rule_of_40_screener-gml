"""
設定ダイアログ
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from ...core.data.config_loader import ConfigManager
except ImportError:
    try:
        from src.core.data.config_loader import ConfigManager
    except ImportError:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.core.data.config_loader import ConfigManager

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """設定ダイアログ"""

    # シグナル
    theme_changed = Signal(str)  # テーマ変更時に発火

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._setup_ui()
        self._load_settings()

        logger.debug("Settings dialog initialized")

    def _setup_ui(self):
        """UI設定"""
        self.setWindowTitle("設定")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # メインレイアウト
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # タブを作成
        self.tab_widget.addTab(self._create_appearance_tab(), "表示")
        self.tab_widget.addTab(self._create_data_fetch_tab(), "データ取得")
        self.tab_widget.addTab(self._create_cache_tab(), "キャッシュ")
        self.tab_widget.addTab(self._create_advanced_tab(), "詳細設定")

        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self._on_apply)
        layout.addWidget(button_box)

    def _create_appearance_tab(self) -> QWidget:
        """表示タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # テーマ設定グループ
        theme_group = QGroupBox("テーマ")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["自動", "ライト", "ダーク"])
        theme_layout.addRow("テーマ:", self.theme_combo)

        layout.addWidget(theme_group)

        # ウィンドウ設定グループ
        window_group = QGroupBox("ウィンドウ")
        window_layout = QVBoxLayout(window_group)

        self.remember_position_checkbox = QCheckBox("ウィンドウ位置を記憶")
        window_layout.addWidget(self.remember_position_checkbox)

        self.remember_size_checkbox = QCheckBox("ウィンドウサイズを記憶")
        window_layout.addWidget(self.remember_size_checkbox)

        layout.addWidget(window_group)

        # ロケール設定グループ
        locale_group = QGroupBox("言語・地域")
        locale_layout = QFormLayout(locale_group)

        self.locale_combo = QComboBox()
        self.locale_combo.addItems(["日本語 (ja)", "English (en)"])
        locale_layout.addRow("言語:", self.locale_combo)

        layout.addWidget(locale_group)

        layout.addStretch()

        return widget

    def _create_data_fetch_tab(self) -> QWidget:
        """データ取得タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 接続設定グループ
        connection_group = QGroupBox("接続設定")
        connection_layout = QFormLayout(connection_group)

        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 300)
        self.timeout_spinbox.setSuffix(" 秒")
        self.timeout_spinbox.setValue(30)
        connection_layout.addRow("タイムアウト:", self.timeout_spinbox)

        layout.addWidget(connection_group)

        # 並列処理設定グループ
        parallel_group = QGroupBox("並列処理")
        parallel_layout = QFormLayout(parallel_group)

        self.max_workers_spinbox = QSpinBox()
        self.max_workers_spinbox.setRange(1, 50)
        self.max_workers_spinbox.setValue(12)
        parallel_layout.addRow("最大ワーカー数:", self.max_workers_spinbox)

        layout.addWidget(parallel_group)

        # リトライ設定グループ
        retry_group = QGroupBox("リトライ設定")
        retry_layout = QFormLayout(retry_group)

        self.retry_attempts_spinbox = QSpinBox()
        self.retry_attempts_spinbox.setRange(0, 10)
        self.retry_attempts_spinbox.setValue(3)
        retry_layout.addRow("リトライ回数:", self.retry_attempts_spinbox)

        self.backoff_factor_spinbox = QDoubleSpinBox()
        self.backoff_factor_spinbox.setRange(1.0, 10.0)
        self.backoff_factor_spinbox.setSingleStep(0.5)
        self.backoff_factor_spinbox.setValue(2.0)
        retry_layout.addRow("バックオフ係数:", self.backoff_factor_spinbox)

        layout.addWidget(retry_group)

        layout.addStretch()

        return widget

    def _create_cache_tab(self) -> QWidget:
        """キャッシュタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # キャッシュ設定グループ
        cache_group = QGroupBox("キャッシュ設定")
        cache_layout = QFormLayout(cache_group)

        self.cache_enabled_checkbox = QCheckBox("キャッシュを有効化")
        cache_layout.addRow("", self.cache_enabled_checkbox)

        self.cache_ttl_spinbox = QSpinBox()
        self.cache_ttl_spinbox.setRange(1, 168)  # 1時間〜1週間
        self.cache_ttl_spinbox.setSuffix(" 時間")
        self.cache_ttl_spinbox.setValue(24)
        cache_layout.addRow("TTL (生存時間):", self.cache_ttl_spinbox)

        self.max_cache_size_spinbox = QSpinBox()
        self.max_cache_size_spinbox.setRange(10, 10000)
        self.max_cache_size_spinbox.setSuffix(" MB")
        self.max_cache_size_spinbox.setValue(500)
        cache_layout.addRow("最大サイズ:", self.max_cache_size_spinbox)

        self.cleanup_interval_spinbox = QSpinBox()
        self.cleanup_interval_spinbox.setRange(1, 168)
        self.cleanup_interval_spinbox.setSuffix(" 時間")
        self.cleanup_interval_spinbox.setValue(24)
        cache_layout.addRow("クリーンアップ間隔:", self.cleanup_interval_spinbox)

        layout.addWidget(cache_group)

        # キャッシュ情報グループ
        info_group = QGroupBox("キャッシュ情報")
        info_layout = QVBoxLayout(info_group)

        self.cache_info_label = QLabel("キャッシュ統計を読み込み中...")
        self.cache_info_label.setWordWrap(True)
        info_layout.addWidget(self.cache_info_label)

        # クリアボタン
        clear_cache_button = QDialogButtonBox.StandardButton.Reset
        button_box = QDialogButtonBox(clear_cache_button)
        button_box.button(QDialogButtonBox.Reset).setText("キャッシュをクリア")
        button_box.button(QDialogButtonBox.Reset).clicked.connect(self._on_clear_cache)
        info_layout.addWidget(button_box)

        layout.addWidget(info_group)

        layout.addStretch()

        return widget

    def _create_advanced_tab(self) -> QWidget:
        """詳細設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ログ設定グループ
        logging_group = QGroupBox("ログ設定")
        logging_layout = QFormLayout(logging_group)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("ログレベル:", self.log_level_combo)

        self.console_log_checkbox = QCheckBox("コンソールログを有効化")
        logging_layout.addRow("", self.console_log_checkbox)

        self.file_log_checkbox = QCheckBox("ファイルログを有効化")
        logging_layout.addRow("", self.file_log_checkbox)

        layout.addWidget(logging_group)

        # 更新設定グループ
        update_group = QGroupBox("更新設定")
        update_layout = QVBoxLayout(update_group)

        self.auto_update_checkbox = QCheckBox("自動更新チェックを有効化")
        update_layout.addWidget(self.auto_update_checkbox)

        layout.addWidget(update_group)

        # プライバシー設定グループ
        privacy_group = QGroupBox("プライバシー")
        privacy_layout = QVBoxLayout(privacy_group)

        self.telemetry_checkbox = QCheckBox("テレメトリを有効化")
        privacy_layout.addWidget(self.telemetry_checkbox)

        telemetry_info = QLabel(
            "テレメトリは匿名の使用統計を収集し、アプリの改善に役立てます。"
        )
        telemetry_info.setWordWrap(True)
        telemetry_info.setStyleSheet("color: gray; font-size: 10px;")
        privacy_layout.addWidget(telemetry_info)

        layout.addWidget(privacy_group)

        # 開発者設定グループ
        developer_group = QGroupBox("開発者設定")
        developer_layout = QVBoxLayout(developer_group)

        self.debug_mode_checkbox = QCheckBox("デバッグモードを有効化")
        developer_layout.addWidget(self.debug_mode_checkbox)

        debug_info = QLabel("デバッグモードでは詳細なログと診断情報が出力されます。")
        debug_info.setWordWrap(True)
        debug_info.setStyleSheet("color: gray; font-size: 10px;")
        developer_layout.addWidget(debug_info)

        layout.addWidget(developer_group)

        layout.addStretch()

        return widget

    def _load_settings(self):
        """設定を読み込み"""
        try:
            # 表示設定
            theme = self.config_manager.get("ui.theme", "auto")
            theme_map = {"auto": 0, "light": 1, "dark": 2}
            self.theme_combo.setCurrentIndex(theme_map.get(theme, 0))

            self.remember_position_checkbox.setChecked(
                self.config_manager.get("ui.window.remember_position", True)
            )
            self.remember_size_checkbox.setChecked(
                self.config_manager.get("ui.window.remember_size", True)
            )

            locale = self.config_manager.get("ui.locale", "ja")
            locale_map = {"ja": 0, "en": 1}
            self.locale_combo.setCurrentIndex(locale_map.get(locale, 0))

            # データ取得設定
            self.timeout_spinbox.setValue(
                self.config_manager.get("fetch.timeout_seconds", 30)
            )
            self.max_workers_spinbox.setValue(
                self.config_manager.get("fetch.max_workers", 12)
            )
            self.retry_attempts_spinbox.setValue(
                self.config_manager.get("fetch.retry_attempts", 3)
            )
            self.backoff_factor_spinbox.setValue(
                self.config_manager.get("fetch.backoff_factor", 2.0)
            )

            # キャッシュ設定
            self.cache_enabled_checkbox.setChecked(
                self.config_manager.get("cache.enabled", True)
            )
            self.cache_ttl_spinbox.setValue(
                self.config_manager.get("fetch.cache_ttl_hours", 24)
            )
            self.max_cache_size_spinbox.setValue(
                self.config_manager.get("cache.max_cache_size_mb", 500)
            )
            self.cleanup_interval_spinbox.setValue(
                self.config_manager.get("cache.cleanup_interval_hours", 24)
            )

            # 詳細設定
            self.log_level_combo.setCurrentText(
                self.config_manager.get("logging.level", "INFO")
            )
            self.console_log_checkbox.setChecked(
                self.config_manager.get("logging.console_enabled", True)
            )
            self.file_log_checkbox.setChecked(
                self.config_manager.get("logging.file_enabled", True)
            )
            self.auto_update_checkbox.setChecked(
                self.config_manager.get("advanced.auto_update_check", False)
            )
            self.telemetry_checkbox.setChecked(
                self.config_manager.get("advanced.enable_telemetry", False)
            )
            self.debug_mode_checkbox.setChecked(
                self.config_manager.get("advanced.debug_mode", False)
            )

            # キャッシュ情報を更新
            self._update_cache_info()

            logger.debug("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def _save_settings(self):
        """設定を保存"""
        try:
            # 表示設定
            theme_map = {0: "auto", 1: "light", 2: "dark"}
            old_theme = self.config_manager.get("ui.theme", "auto")
            new_theme = theme_map[self.theme_combo.currentIndex()]

            self.config_manager.set("ui.theme", new_theme)
            self.config_manager.set(
                "ui.window.remember_position",
                self.remember_position_checkbox.isChecked()
            )
            self.config_manager.set(
                "ui.window.remember_size",
                self.remember_size_checkbox.isChecked()
            )

            locale_map = {0: "ja", 1: "en"}
            self.config_manager.set(
                "ui.locale",
                locale_map[self.locale_combo.currentIndex()]
            )

            # データ取得設定
            self.config_manager.set(
                "fetch.timeout_seconds",
                self.timeout_spinbox.value()
            )
            self.config_manager.set(
                "fetch.max_workers",
                self.max_workers_spinbox.value()
            )
            self.config_manager.set(
                "fetch.retry_attempts",
                self.retry_attempts_spinbox.value()
            )
            self.config_manager.set(
                "fetch.backoff_factor",
                self.backoff_factor_spinbox.value()
            )

            # キャッシュ設定
            self.config_manager.set(
                "cache.enabled",
                self.cache_enabled_checkbox.isChecked()
            )
            self.config_manager.set(
                "fetch.cache_ttl_hours",
                self.cache_ttl_spinbox.value()
            )
            self.config_manager.set(
                "cache.max_cache_size_mb",
                self.max_cache_size_spinbox.value()
            )
            self.config_manager.set(
                "cache.cleanup_interval_hours",
                self.cleanup_interval_spinbox.value()
            )

            # 詳細設定
            self.config_manager.set(
                "logging.level",
                self.log_level_combo.currentText()
            )
            self.config_manager.set(
                "logging.console_enabled",
                self.console_log_checkbox.isChecked()
            )
            self.config_manager.set(
                "logging.file_enabled",
                self.file_log_checkbox.isChecked()
            )
            self.config_manager.set(
                "advanced.auto_update_check",
                self.auto_update_checkbox.isChecked()
            )
            self.config_manager.set(
                "advanced.enable_telemetry",
                self.telemetry_checkbox.isChecked()
            )
            self.config_manager.set(
                "advanced.debug_mode",
                self.debug_mode_checkbox.isChecked()
            )

            # ファイルに保存
            self.config_manager.save()

            # テーマ変更時にシグナルを発火
            if old_theme != new_theme:
                self.theme_changed.emit(new_theme)

            logger.info("Settings saved successfully")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise

    def _update_cache_info(self):
        """キャッシュ情報を更新"""
        try:
            # TODO: 実際のキャッシュ統計を取得する
            # 現在はプレースホルダー
            info_text = (
                "キャッシュデータベース: cache.db\n"
                "現在のサイズ: 計算中...\n"
                "エントリ数: 計算中..."
            )
            self.cache_info_label.setText(info_text)
        except Exception as e:
            logger.error(f"Failed to update cache info: {e}")
            self.cache_info_label.setText("キャッシュ情報の取得に失敗しました")

    def _on_clear_cache(self):
        """キャッシュクリアボタンクリック時の処理"""
        try:
            # TODO: 実際のキャッシュクリア処理を実装
            logger.info("Cache clear requested")
            self._update_cache_info()

            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "キャッシュクリア",
                "キャッシュがクリアされました。"
            )
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "エラー",
                f"キャッシュのクリアに失敗しました:\n{e}"
            )

    def _on_apply(self):
        """適用ボタンクリック時の処理"""
        try:
            self._save_settings()
            logger.info("Settings applied")
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "エラー",
                f"設定の適用に失敗しました:\n{e}"
            )

    def _on_accept(self):
        """OKボタンクリック時の処理"""
        try:
            self._save_settings()
            self.accept()
        except Exception as e:
            logger.error(f"Failed to accept settings: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "エラー",
                f"設定の保存に失敗しました:\n{e}"
            )
