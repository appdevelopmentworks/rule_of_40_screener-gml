"""
結果表示テーブルウィジェット
"""

import logging
from typing import List, Optional

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from ...core.domain.models import CalculationPeriod, Rule40Result, Rule40Variant
except ImportError:
    try:
        from src.core.domain.models import (
            CalculationPeriod,
            Rule40Result,
            Rule40Variant,
        )
    except ImportError:
        # Fallback for direct execution
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.core.domain.models import (
            Rule40Result,
            Rule40Variant,
        )

logger = logging.getLogger(__name__)


class ResultsTable(QWidget):
    """スクリーニング結果表示テーブル"""

    # シグナル
    row_selected = Signal(Rule40Result)
    filter_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results: List[Rule40Result] = []
        self.filtered_results: List[Rule40Result] = []
        self.current_variant = Rule40Variant.OP

        self._setup_ui()
        self._setup_connections()

        logger.debug("Results table initialized")

    def _setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ヘッダーコントロール
        header_widget = self._create_header_widget()
        layout.addWidget(header_widget)

        # テーブル
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)

        # ヘッダー設定
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 列設定
        self._setup_columns()

        layout.addWidget(self.table)

        # フッター（統計情報）
        footer_widget = self._create_footer_widget()
        layout.addWidget(footer_widget)

    def _create_header_widget(self) -> QWidget:
        """ヘッダーコントロール作成"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # バリアント選択
        layout.addWidget(QLabel("表示:"))
        self.variant_combo = QComboBox()
        self.variant_combo.addItems(["営業利益版", "EBITDA版", "両方"])
        self.variant_combo.setCurrentIndex(0)
        layout.addWidget(self.variant_combo)

        layout.addStretch()

        # 検索ボックス
        layout.addWidget(QLabel("検索:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("銘柄名やシンボルで検索...")
        self.search_box.setMaximumWidth(200)
        layout.addWidget(self.search_box)

        # 閾値フィルター
        self.threshold_checkbox = QCheckBox("40%以上のみ")
        self.threshold_checkbox.setChecked(True)
        layout.addWidget(self.threshold_checkbox)

        # リフレッシュボタン
        self.refresh_button = QPushButton("更新")
        self.refresh_button.setMaximumWidth(80)
        layout.addWidget(self.refresh_button)

        return widget

    def _create_footer_widget(self) -> QWidget:
        """フッター統計情報作成"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stats_label = QLabel("結果: 0件")
        layout.addWidget(self.stats_label)

        layout.addStretch()

        self.filtered_label = QLabel("表示: 0件")
        layout.addWidget(self.filtered_label)

        # CSVエクスポートボタン
        self.export_csv_button = QPushButton("CSV出力")
        self.export_csv_button.setMaximumWidth(120)
        self.export_csv_button.setToolTip("表示中の結果をCSVファイルにエクスポート")
        self.export_csv_button.setEnabled(False)  # 初期状態は無効
        layout.addWidget(self.export_csv_button)

        return widget

    def _setup_columns(self):
        """列設定"""
        columns = [
            "シンボル",
            "銘柄名",
            "Rule of 40",
            "売上成長率",
            "営業利益率",
            "EBITDAマージン",
            "時価総額",
            "セクター",
        ]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # 列幅設定
        column_widths = [80, 200, 100, 100, 100, 100, 100, 150]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)

    def _setup_connections(self):
        """シグナル接続"""
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.variant_combo.currentTextChanged.connect(self._on_variant_changed)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.threshold_checkbox.toggled.connect(self._on_threshold_changed)
        self.refresh_button.clicked.connect(self.refresh_display)
        self.export_csv_button.clicked.connect(self._on_export_csv)

    def set_results(self, results: List[Rule40Result]):
        """結果を設定"""
        self.results = results
        self._apply_filters()
        self.refresh_display()

        # 結果があればエクスポートボタンを有効化
        self.export_csv_button.setEnabled(len(results) > 0)

        logger.info(f"Set {len(results)} results in table")

    def _apply_filters(self):
        """フィルター適用"""
        filtered = self.results.copy()

        # バリアントフィルター
        if self.current_variant == Rule40Variant.OP:
            filtered = [r for r in filtered if r.r40_op is not None]
        elif self.current_variant == Rule40Variant.EBITDA:
            filtered = [r for r in filtered if r.r40_ebitda is not None]

        # 閾値フィルター
        if self.threshold_checkbox.isChecked():
            threshold = 40.0
            if self.current_variant == Rule40Variant.OP:
                filtered = [r for r in filtered if r.r40_op and r.r40_op >= threshold]
            elif self.current_variant == Rule40Variant.EBITDA:
                filtered = [
                    r for r in filtered if r.r40_ebitda and r.r40_ebitda >= threshold
                ]
            else:  # BOTH
                filtered = [
                    r
                    for r in filtered
                    if (r.r40_op and r.r40_op >= threshold)
                    or (r.r40_ebitda and r.r40_ebitda >= threshold)
                ]

        # 検索フィルター
        search_text = self.search_box.text().strip().lower()
        if search_text:
            filtered = [
                r
                for r in filtered
                if search_text in r.symbol.lower()
                or search_text in r.name.lower()
                or search_text in r.sector.lower()
            ]

        self.filtered_results = filtered

        # 統計更新
        self.stats_label.setText(f"結果: {len(self.results)}件")
        self.filtered_label.setText(f"表示: {len(self.filtered_results)}件")

    def refresh_display(self):
        """表示更新"""
        self.table.setRowCount(len(self.filtered_results))

        for row, result in enumerate(self.filtered_results):
            # シンボル
            self.table.setItem(row, 0, self._create_item(result.symbol))

            # 銘柄名
            self.table.setItem(row, 1, self._create_item(result.name))

            # Rule of 40
            r40_value = result.get_r40_value(self.current_variant)
            r40_item = self._create_numeric_item(
                r40_value, "%.1f%%" % r40_value if r40_value else "N/A"
            )
            if r40_value and r40_value >= 40:
                r40_item.setBackground(Qt.green)
            elif r40_value and r40_value >= 30:
                r40_item.setBackground(Qt.yellow)
            self.table.setItem(row, 2, r40_item)

            # 売上成長率
            growth_item = self._create_numeric_item(
                result.revenue_growth_yoy,
                (
                    "%.1f%%" % (result.revenue_growth_yoy * 100)
                    if result.revenue_growth_yoy
                    else "N/A"
                ),
            )
            self.table.setItem(row, 3, growth_item)

            # 営業利益率
            op_item = self._create_numeric_item(
                result.operating_margin,
                (
                    "%.1f%%" % (result.operating_margin * 100)
                    if result.operating_margin
                    else "N/A"
                ),
            )
            self.table.setItem(row, 4, op_item)

            # EBITDAマージン
            ebitda_item = self._create_numeric_item(
                result.ebitda_margin,
                (
                    "%.1f%%" % (result.ebitda_margin * 100)
                    if result.ebitda_margin
                    else "N/A"
                ),
            )
            self.table.setItem(row, 5, ebitda_item)

            # 時価総額
            mc_item = self._create_numeric_item(
                result.market_cap,
                (
                    self._format_market_cap(result.market_cap)
                    if result.market_cap
                    else "N/A"
                ),
            )
            self.table.setItem(row, 6, mc_item)

            # セクター
            self.table.setItem(row, 7, self._create_item(result.sector))

        logger.debug(f"Refreshed display with {len(self.filtered_results)} rows")

    def _create_item(self, text: str) -> QTableWidgetItem:
        """テーブルアイテム作成"""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _create_numeric_item(
        self, value: Optional[float], formatted_text: str
    ) -> QTableWidgetItem:
        """数値アイテム作成"""
        item = QTableWidgetItem(formatted_text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        if value is not None:
            item.setData(Qt.UserRole, value)  # ソート用に生データを保持

            # 負値は赤色
            if value < 0:
                item.setForeground(Qt.red)

        return item

    def _format_market_cap(self, market_cap: float) -> str:
        """時価総額をフォーマット"""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.1f}M"
        else:
            return f"${market_cap:,.0f}"

    def _on_selection_changed(self):
        """選択変更イベント"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.filtered_results):
            result = self.filtered_results[current_row]
            self.row_selected.emit(result)

    def _on_variant_changed(self, text: str):
        """バリアント変更イベント"""
        variant_map = {
            "営業利益版": Rule40Variant.OP,
            "EBITDA版": Rule40Variant.EBITDA,
            "両方": Rule40Variant.BOTH,
        }
        self.current_variant = variant_map.get(text, Rule40Variant.OP)
        self._apply_filters()
        self.refresh_display()

    def _on_search_changed(self, text: str):
        """検索テキスト変更イベント"""
        self._apply_filters()
        self.refresh_display()

    def _on_threshold_changed(self, checked: bool):
        """閾値チェック変更イベント"""
        self._apply_filters()
        self.refresh_display()

    def get_selected_result(self) -> Optional[Rule40Result]:
        """選択中の結果を取得"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.filtered_results):
            return self.filtered_results[current_row]
        return None

    def clear_results(self):
        """結果をクリア"""
        self.results.clear()
        self.filtered_results.clear()
        self.table.setRowCount(0)
        self.stats_label.setText("結果: 0件")
        self.filtered_label.setText("表示: 0件")

    def export_to_dataframe(self) -> pd.DataFrame:
        """DataFrameにエクスポート"""
        if not self.filtered_results:
            return pd.DataFrame()

        data = []
        for result in self.filtered_results:
            row = {
                "シンボル": result.symbol,
                "銘柄名": result.name,
                "Rule of 40 (OP)": result.r40_op,
                "Rule of 40 (EBITDA)": result.r40_ebitda,
                "売上成長率": result.revenue_growth_yoy,
                "営業利益率": result.operating_margin,
                "EBITDAマージン": result.ebitda_margin,
                "時価総額": result.market_cap,
                "セクター": result.sector,
                "業種": result.industry,
                "データ品質": result.data_quality.value,
                "計算時刻": result.calculation_time,
            }
            data.append(row)

        return pd.DataFrame(data)

    def _on_export_csv(self):
        """CSVエクスポートボタンクリック"""
        from datetime import datetime
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        # 結果がない場合
        if not self.filtered_results:
            QMessageBox.warning(self, "警告", "エクスポートする結果がありません")
            return

        # ファイル保存ダイアログ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"rule40_results_{timestamp}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSV形式でエクスポート",
            default_filename,
            "CSVファイル (*.csv);;すべてのファイル (*.*)"
        )

        if not file_path:
            return

        try:
            # DataFrameに変換してCSVエクスポート
            df = self.export_to_dataframe()
            df.to_csv(file_path, index=False, encoding="utf-8-sig")

            QMessageBox.information(
                self,
                "エクスポート完了",
                f"結果をエクスポートしました:\n{file_path}\n\n件数: {len(self.filtered_results)}件"
            )

            logger.info(f"Exported {len(self.filtered_results)} results to CSV: {file_path}")

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            QMessageBox.critical(
                self,
                "エクスポートエラー",
                f"CSVエクスポートに失敗しました:\n{e}"
            )
