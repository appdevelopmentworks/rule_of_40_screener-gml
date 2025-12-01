"""
サイドバーウィジェット
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

try:
    from ...core.data.config_loader import ConfigManager
    from ...core.domain.models import CalculationPeriod, Rule40Variant, ScreeningConfig
except ImportError:
    try:
        from src.core.data.config_loader import ConfigManager
        from src.core.domain.models import (
            CalculationPeriod,
            Rule40Variant,
            ScreeningConfig,
        )
    except ImportError:
        # Fallback for direct execution
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.core.data.config_loader import ConfigManager
        from src.core.domain.models import (
            CalculationPeriod,
            Rule40Variant,
            ScreeningConfig,
        )

logger = logging.getLogger(__name__)


class SideBar(QWidget):
    """サイドバーウィジェット"""

    # シグナル
    start_screening = Signal(ScreeningConfig)
    stop_screening = Signal()
    config_changed = Signal(ScreeningConfig)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._setup_ui()
        self._load_config()
        self._connect_signals()

        logger.debug("Side bar initialized")

    def _setup_ui(self):
        """UI設定"""
        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # コンテンツウィジェット
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # メインレイアウト
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(scroll_area)

        # コンテンツレイアウト
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(10)

        # ユニバース選択
        content_layout.addWidget(self._create_universe_group())

        # Rule of 40 設定
        content_layout.addWidget(self._create_rule40_group())

        # フィルター設定
        content_layout.addWidget(self._create_filter_group())

        # データ取得設定
        content_layout.addWidget(self._create_fetch_group())

        # 実行ボタン
        content_layout.addWidget(self._create_action_buttons())

        content_layout.addStretch()

    def _create_universe_group(self) -> QGroupBox:
        """ユニバース選択グループ"""
        group = QGroupBox("ユニバース選択")
        layout = QVBoxLayout(group)

        # データソース選択
        self.sp500_checkbox = QCheckBox("S&P 500")
        self.sp500_checkbox.setChecked(True)
        layout.addWidget(self.sp500_checkbox)

        self.sp400_checkbox = QCheckBox("S&P 400")
        self.sp400_checkbox.setChecked(False)
        layout.addWidget(self.sp400_checkbox)

        self.nasdaq100_checkbox = QCheckBox("Nasdaq 100")
        self.nasdaq100_checkbox.setChecked(False)
        layout.addWidget(self.nasdaq100_checkbox)

        self.nasdaq_checkbox = QCheckBox("Nasdaq 全銘柄")
        self.nasdaq_checkbox.setChecked(False)
        layout.addWidget(self.nasdaq_checkbox)

        self.other_checkbox = QCheckBox("その他上場銘柄")
        self.other_checkbox.setChecked(False)
        layout.addWidget(self.other_checkbox)

        self.jpx_checkbox = QCheckBox("日本株（東証）")
        self.jpx_checkbox.setChecked(False)
        layout.addWidget(self.jpx_checkbox)

        # CSVファイル
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(QLabel("CSVファイル:"))
        self.csv_checkbox = QCheckBox("使用する")
        csv_layout.addWidget(self.csv_checkbox)
        layout.addLayout(csv_layout)

        return group

    def _create_rule40_group(self) -> QGroupBox:
        """Rule of 40 設定グループ"""
        group = QGroupBox("Rule of 40 設定")
        layout = QVBoxLayout(group)

        # バリアント選択
        variant_layout = QHBoxLayout()
        variant_layout.addWidget(QLabel("計算方式:"))
        self.variant_combo = QComboBox()
        self.variant_combo.addItems(["営業利益版", "EBITDA版", "両方"])
        self.variant_combo.setCurrentIndex(0)
        variant_layout.addWidget(self.variant_combo)
        layout.addLayout(variant_layout)

        # 期間選択
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("計算期間:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["TTM (12ヶ月)", "年次", "四半期年率"])
        self.period_combo.setCurrentIndex(0)
        period_layout.addWidget(self.period_combo)
        layout.addLayout(period_layout)

        # 閾値設定
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("閾値:"))
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0, 200)
        self.threshold_spinbox.setValue(40.0)
        self.threshold_spinbox.setSuffix("%")
        threshold_layout.addWidget(self.threshold_spinbox)
        layout.addLayout(threshold_layout)

        return group

    def _create_filter_group(self) -> QGroupBox:
        """フィルター設定グループ"""
        group = QGroupBox("フィルター設定")
        layout = QVBoxLayout(group)

        # 最小売上高
        revenue_layout = QHBoxLayout()
        revenue_layout.addWidget(QLabel("最小売上高:"))
        self.min_revenue_spinbox = QDoubleSpinBox()
        self.min_revenue_spinbox.setRange(0, 1000)
        self.min_revenue_spinbox.setValue(0.1)
        self.min_revenue_spinbox.setSuffix("B $")
        self.min_revenue_spinbox.setSpecialValueText("なし")
        revenue_layout.addWidget(self.min_revenue_spinbox)
        layout.addLayout(revenue_layout)

        # マージン条件
        self.margin_positive_checkbox = QCheckBox("黒字銘柄のみ")
        self.margin_positive_checkbox.setChecked(False)
        layout.addWidget(self.margin_positive_checkbox)

        # 除外銘柄
        exclude_layout = QVBoxLayout()
        exclude_layout.addWidget(QLabel("除外銘柄 (カンマ区切り):"))
        self.exclude_checkbox = QCheckBox("除外リストを使用")
        self.exclude_edit = QLabel("例: BRK-A, BRK-B")
        self.exclude_edit.setWordWrap(True)
        self.exclude_edit.setStyleSheet(
            "QLabel { background-color: #f0f0f0; padding: 5px; }"
        )
        exclude_layout.addWidget(self.exclude_checkbox)
        exclude_layout.addWidget(self.exclude_edit)
        layout.addLayout(exclude_layout)

        return group

    def _create_fetch_group(self) -> QGroupBox:
        """データ取得設定グループ"""
        group = QGroupBox("データ取得設定")
        layout = QVBoxLayout(group)

        # 並列数
        workers_layout = QHBoxLayout()
        workers_layout.addWidget(QLabel("並列数:"))
        self.workers_spinbox = QSpinBox()
        self.workers_spinbox.setRange(1, 50)
        self.workers_spinbox.setValue(12)
        workers_layout.addWidget(self.workers_spinbox)
        layout.addLayout(workers_layout)

        # キャッシュ期間
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("キャッシュ期間:"))
        self.cache_spinbox = QSpinBox()
        self.cache_spinbox.setRange(1, 168)  # 1時間〜1週間
        self.cache_spinbox.setValue(24)
        self.cache_spinbox.setSuffix("時間")
        cache_layout.addWidget(self.cache_spinbox)
        layout.addLayout(cache_layout)

        # 強制更新
        self.force_refresh_checkbox = QCheckBox("強制更新（キャッシュ無視）")
        self.force_refresh_checkbox.setChecked(False)
        layout.addWidget(self.force_refresh_checkbox)

        return group

    def _create_action_buttons(self) -> QWidget:
        """アクションボタン作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)

        # スクリーニング開始ボタン
        self.start_button = QPushButton("スクリーニング開始")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        layout.addWidget(self.start_button)

        # 停止ボタン
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        layout.addWidget(self.stop_button)

        # 設定保存ボタン
        self.save_config_button = QPushButton("設定を保存")
        layout.addWidget(self.save_config_button)

        return widget

    def _load_config(self):
        """設定を読み込み"""
        try:
            # ユニバース設定
            sources = self.config_manager.get("universe.sources", ["sp500"])
            self.sp500_checkbox.setChecked("sp500" in sources)
            self.sp400_checkbox.setChecked("sp400" in sources)
            self.nasdaq100_checkbox.setChecked("nasdaq100" in sources)
            self.nasdaq_checkbox.setChecked("nasdaq" in sources)
            self.other_checkbox.setChecked("other" in sources)
            self.jpx_checkbox.setChecked("jpx" in sources)

            # Rule of 40 設定
            variant = self.config_manager.get("rule40.variant", "op")
            variant_map = {"op": 0, "ebitda": 1, "both": 2}
            self.variant_combo.setCurrentIndex(variant_map.get(variant, 0))

            period = self.config_manager.get("rule40.period", "ttm")
            period_map = {"ttm": 0, "annual": 1, "mrq_annualized": 2}
            self.period_combo.setCurrentIndex(period_map.get(period, 0))

            self.threshold_spinbox.setValue(
                self.config_manager.get("rule40.threshold", 40.0)
            )

            # フィルター設定
            self.min_revenue_spinbox.setValue(
                self.config_manager.get("filter.min_revenue", 0.1)
            )
            self.margin_positive_checkbox.setChecked(
                self.config_manager.get("filter.margin_positive_only", False)
            )

            # データ取得設定
            self.workers_spinbox.setValue(
                self.config_manager.get("fetch.max_workers", 12)
            )
            self.cache_spinbox.setValue(
                self.config_manager.get("fetch.cache_ttl_hours", 24)
            )
            self.force_refresh_checkbox.setChecked(
                self.config_manager.get("fetch.force_refresh", False)
            )

        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    def get_screening_config(self) -> ScreeningConfig:
        """スクリーニング設定を取得"""
        # データソース
        sources = []
        if self.sp500_checkbox.isChecked():
            sources.append("sp500")
        if self.sp400_checkbox.isChecked():
            sources.append("sp400")
        if self.nasdaq100_checkbox.isChecked():
            sources.append("nasdaq100")
        if self.nasdaq_checkbox.isChecked():
            sources.append("nasdaq")
        if self.other_checkbox.isChecked():
            sources.append("other")
        if self.jpx_checkbox.isChecked():
            sources.append("jpx")

        # バリアント
        variant_map = {
            0: Rule40Variant.OP,
            1: Rule40Variant.EBITDA,
            2: Rule40Variant.BOTH,
        }
        variant = variant_map[self.variant_combo.currentIndex()]

        # 期間
        period_map = {
            0: CalculationPeriod.TTM,
            1: CalculationPeriod.ANNUAL,
            2: CalculationPeriod.MRQ_ANNUALIZED,
        }
        period = period_map[self.period_combo.currentIndex()]

        # 除外銘柄
        exclude_symbols = []
        if hasattr(self, "exclude_checkbox") and self.exclude_checkbox.isChecked():
            exclude_text = (
                self.exclude_edit.text()
                if hasattr(self.exclude_edit, "text")
                else str(self.exclude_edit.text())
            )
            if exclude_text:
                exclude_symbols = [
                    s.strip().upper() for s in exclude_text.split(",") if s.strip()
                ]

        return ScreeningConfig(
            sources=sources,
            variant=variant,
            period=period,
            threshold=self.threshold_spinbox.value(),
            min_revenue=(
                self.min_revenue_spinbox.value() * 1e9
                if self.min_revenue_spinbox.value() > 0
                else None
            ),
            margin_positive_only=self.margin_positive_checkbox.isChecked(),
            exclude_symbols=exclude_symbols,
            max_workers=self.workers_spinbox.value(),
            cache_ttl_hours=self.cache_spinbox.value(),
            force_refresh=self.force_refresh_checkbox.isChecked(),
        )

    def set_processing(self, is_processing: bool):
        """処理状態を設定"""
        self.start_button.setEnabled(not is_processing)
        self.stop_button.setEnabled(is_processing)

        if is_processing:
            self.start_button.setText("処理中...")
        else:
            self.start_button.setText("スクリーニング開始")

    def load_csv_file(self, file_path: str):
        """CSVファイルを読み込んで設定"""
        try:
            # CSVチェックボックスをオンにする
            self.csv_checkbox.setChecked(True)

            # CSVファイルパスを保存（実際の処理はscreening_serviceで行う）
            self.csv_file_path = file_path

            # ステータス更新
            logger.info(f"CSV file loaded: {file_path}")

        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise

    def _connect_signals(self):
        """シグナル接続"""
        # スクリーニング開始ボタン
        self.start_button.clicked.connect(self._on_start_screening)
        
        # 停止ボタン
        self.stop_button.clicked.connect(self._on_stop_screening)

    def _on_start_screening(self):
        """スクリーニング開始処理"""
        try:
            # 設定からScreeningConfigを作成
            config = self._create_screening_config()
            
            # シグナル発行
            self.start_screening.emit(config)
            
            logger.info("Screening started")
            
        except Exception as e:
            logger.error(f"Failed to start screening: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "エラー", f"スクリーニング開始に失敗しました:\n{e}")

    def _on_stop_screening(self):
        """スクリーニング停止処理"""
        try:
            # シグナル発行
            self.stop_screening.emit()
            
            logger.info("Screening stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop screening: {e}")

    def _create_screening_config(self):
        """現在のUI設定からScreeningConfigを作成"""
        try:
            from ...core.domain.models import ScreeningConfig, Filter
        except ImportError:
            try:
                from src.core.domain.models import ScreeningConfig, Filter
            except ImportError:
                # Fallback for direct execution
                import sys
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent
                sys.path.insert(0, str(project_root))
                from src.core.domain.models import ScreeningConfig, Filter
        
        # ユニバース設定
        sources = []
        if self.sp500_checkbox.isChecked():
            sources.append("sp500")
        if self.sp400_checkbox.isChecked():
            sources.append("sp400")
        if self.nasdaq100_checkbox.isChecked():
            sources.append("nasdaq100")
        if self.nasdaq_checkbox.isChecked():
            sources.append("nasdaq")
        if self.other_checkbox.isChecked():
            sources.append("other")
        if self.csv_checkbox.isChecked():
            sources.append("csv")
        
        # Rule of 40 設定
        variant_map = {0: "op", 1: "ebitda", 2: "both"}
        period_map = {0: "ttm", 1: "annual", 2: "mrq_annualized"}
        
        # フィルター設定（カスタムフィルターは現在なし）
        filters = []

        config = ScreeningConfig(
            sources=sources,
            csv_path=getattr(self, 'csv_file_path', None),
            variant=Rule40Variant(variant_map[self.variant_combo.currentIndex()]),
            period=CalculationPeriod(period_map[self.period_combo.currentIndex()]),
            threshold=self.threshold_spinbox.value(),
            filters=filters,
            min_revenue=self.min_revenue_spinbox.value() * 1_000_000 if self.min_revenue_spinbox.value() > 0 else None,
            margin_positive_only=self.margin_positive_checkbox.isChecked(),
            max_workers=max(1, self.workers_spinbox.value()),  # 最小値1を保証
            cache_ttl_hours=max(1, self.cache_spinbox.value()),  # 最小値1を保証
            force_refresh=self.force_refresh_checkbox.isChecked()
        )
        
        return config
