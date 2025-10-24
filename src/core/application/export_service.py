"""
エクスポートサービス
"""

import csv
import logging
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd

try:
    from ..domain.models import ExportConfig, ExportError, Rule40Result
except ImportError:
    from src.core.domain.models import ExportConfig, ExportError, Rule40Result

logger = logging.getLogger(__name__)


class ExportService:
    """エクスポートサービス"""

    def __init__(self):
        self.supported_formats = ["csv", "xlsx", "json"]

    def export_results(
        self,
        results: List[Rule40Result],
        config: ExportConfig,
        file_path: Optional[str] = None,
    ) -> str:
        """結果をエクスポート"""
        try:
            # ファイルパス決定
            if file_path is None:
                file_path = self._generate_file_path(config)

            # ディレクトリ作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # フォーマットに応じてエクスポート
            if config.format.lower() == "csv":
                self._export_csv(results, config, file_path)
            elif config.format.lower() == "xlsx":
                self._export_excel(results, config, file_path)
            elif config.format.lower() == "json":
                self._export_json(results, config, file_path)
            else:
                raise ExportError(f"Unsupported format: {config.format}")

            logger.info(f"Successfully exported {len(results)} results to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise ExportError(f"Failed to export results: {e}")

    def _generate_file_path(self, config: ExportConfig) -> str:
        """ファイルパスを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if config.file_path:
            # 指定されたパスを使用
            base_path = config.file_path
            if os.path.isdir(base_path):
                filename = f"rule40_results_{timestamp}.{config.format}"
                return os.path.join(base_path, filename)
            else:
                return base_path
        else:
            # デフォルトパス
            filename = f"rule40_results_{timestamp}.{config.format}"
            return os.path.join("exports", filename)

    def _export_csv(
        self, results: List[Rule40Result], config: ExportConfig, file_path: str
    ):
        """CSV形式でエクスポート"""
        # データフレーム作成
        df = self._create_dataframe(results, config)

        # CSV出力
        df.to_csv(
            file_path,
            index=False,
            encoding=config.encoding,
            sep=config.csv_delimiter,
            float_format=f"%.{config.decimal_places}f",
        )

        # メタデータ追加
        if config.include_metadata:
            self._add_csv_metadata(file_path, config, len(results))

    def _export_excel(
        self, results: List[Rule40Result], config: ExportConfig, file_path: str
    ):
        """Excel形式でエクスポート"""
        # データフレーム作成
        df = self._create_dataframe(results, config)

        # Excelライター作成
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # メインデータ
            df.to_excel(
                writer,
                sheet_name=config.excel_sheet_name,
                index=False,
                float_format=f"%.{config.decimal_places}f",
            )

            # メタデータシート
            if config.include_metadata:
                metadata_df = self._create_metadata_dataframe(config, len(results))
                metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

            # 列幅調整
            worksheet = writer.sheets[config.excel_sheet_name]
            self._adjust_column_width(worksheet, df)

    def _export_json(
        self, results: List[Rule40Result], config: ExportConfig, file_path: str
    ):
        """JSON形式でエクスポート"""
        data = {
            "metadata": (
                self._create_metadata_dict(config, len(results))
                if config.include_metadata
                else None
            ),
            "results": [self._result_to_dict(result, config) for result in results],
        }

        # メタデータを除外
        if not config.include_metadata:
            data.pop("metadata")

        df = pd.DataFrame(data)
        df.to_json(
            file_path, orient="records", indent=2, force_ascii=False, date_format="iso"
        )

    def _create_dataframe(
        self, results: List[Rule40Result], config: ExportConfig
    ) -> pd.DataFrame:
        """データフレーム作成"""
        data = []

        for result in results:
            row = {
                "シンボル": result.symbol,
                "銘柄名": result.name,
                "Rule of 40 (OP)": self._format_value(result.r40_op, config),
                "Rule of 40 (EBITDA)": self._format_value(result.r40_ebitda, config),
                "売上成長率 (%)": self._format_value(
                    (
                        result.revenue_growth_yoy * 100
                        if result.revenue_growth_yoy
                        else None
                    ),
                    config,
                ),
                "営業利益率 (%)": self._format_value(
                    result.operating_margin * 100 if result.operating_margin else None,
                    config,
                ),
                "EBITDAマージン (%)": self._format_value(
                    result.ebitda_margin * 100 if result.ebitda_margin else None, config
                ),
                "時価総額 (B$)": self._format_value(
                    result.market_cap / 1e9 if result.market_cap else None, config
                ),
                "セクター": result.sector,
                "業種": result.industry,
                "データ品質": result.data_quality.value,
                "計算時刻": (
                    result.calculation_time.isoformat()
                    if result.calculation_time
                    else None
                ),
            }
            data.append(row)

        return pd.DataFrame(data)

    def _format_value(
        self, value: Optional[float], config: ExportConfig
    ) -> Optional[str]:
        """値をフォーマット"""
        if value is None:
            return None

        if config.decimal_places == 0:
            return f"{value:.0f}"
        else:
            return f"{value:.{config.decimal_places}f}"

    def _result_to_dict(self, result: Rule40Result, config: ExportConfig) -> dict:
        """結果を辞書に変換"""
        return {
            "symbol": result.symbol,
            "name": result.name,
            "r40_op": result.r40_op,
            "r40_ebitda": result.r40_ebitda,
            "revenue_growth_yoy": result.revenue_growth_yoy,
            "operating_margin": result.operating_margin,
            "ebitda_margin": result.ebitda_margin,
            "market_cap": result.market_cap,
            "sector": result.sector,
            "industry": result.industry,
            "data_quality": result.data_quality.value,
            "period": result.period.value,
            "variant": result.variant.value,
            "calculation_time": (
                result.calculation_time.isoformat() if result.calculation_time else None
            ),
        }

    def _create_metadata_dataframe(
        self, config: ExportConfig, result_count: int
    ) -> pd.DataFrame:
        """メタデータデータフレーム作成"""
        metadata = self._create_metadata_dict(config, result_count)
        return pd.DataFrame(list(metadata.items()), columns=["項目", "値"])

    def _create_metadata_dict(self, config: ExportConfig, result_count: int) -> dict:
        """メタデータ辞書作成"""
        return {
            "エクスポート時刻": datetime.now().isoformat(),
            "結果件数": result_count,
            "エクスポート形式": config.format.upper(),
            "小数点桁数": config.decimal_places,
            "エンコーディング": config.encoding,
            "アプリケーション": "Rule of 40 Screener",
            "バージョン": "0.1.0",
        }

    def _add_csv_metadata(
        self, file_path: str, config: ExportConfig, result_count: int
    ):
        """CSVにメタデータを追加"""
        metadata = self._create_metadata_dict(config, result_count)

        with open(file_path, "a", encoding=config.encoding, newline="") as f:
            writer = csv.writer(f)
            writer.writerow([])  # 空行
            writer.writerow(["# メタデータ"])
            for key, value in metadata.items():
                writer.writerow([f"# {key}", value])

    def _adjust_column_width(self, worksheet, df: pd.DataFrame):
        """Excelの列幅を調整"""
        for column in df.columns:
            column_length = max(df[column].astype(str).map(len).max(), len(str(column)))
            # 最小幅と最大幅を設定
            column_length = max(10, min(column_length + 2, 50))

            # 列番号を取得
            col_idx = df.columns.get_loc(column) + 1
            worksheet.column_dimensions[
                worksheet.cell(row=1, column=col_idx).column_letter
            ].width = column_length

    def get_preview(
        self, results: List[Rule40Result], config: ExportConfig, max_rows: int = 10
    ) -> pd.DataFrame:
        """エクスポートプレビューを取得"""
        if not results:
            return pd.DataFrame()

        # 先頭数行のみ
        preview_results = results[:max_rows]
        return self._create_dataframe(preview_results, config)

    def validate_export_path(self, file_path: str) -> bool:
        """エクスポートパスをバリデーション"""
        try:
            # ディレクトリの書き込み権限チェック
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # ファイルの書き込み権限チェック
            with open(file_path, "w") as f:
                f.write("")
            os.remove(file_path)

            return True
        except Exception as e:
            logger.warning(f"Export path validation failed: {e}")
            return False
