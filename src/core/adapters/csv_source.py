"""
CSV ファイル銘柄データ取得アダプタ
"""

import logging
from typing import List, Union

import pandas as pd

try:
    from ...domain.models import Market, Symbol
    from .base import BaseSymbolSource, DataSourceError, ParseError
except ImportError:
    from src.core.adapters.base import BaseSymbolSource, DataSourceError, ParseError
    from src.core.domain.models import Market, Symbol


logger = logging.getLogger(__name__)


class CSVFileSource(BaseSymbolSource):
    """CSV ファイルから銘柄を取得"""

    def __init__(
        self,
        file_path: str,
        symbol_col: Union[str, int] = "symbol",
        name_col: Union[str, int] = "name",
        auto_add_exchange_suffix: bool = True
    ):
        super().__init__(f"CSV File: {file_path}")
        self.file_path = file_path
        self.symbol_col = symbol_col
        self.name_col = name_col
        self.auto_add_exchange_suffix = auto_add_exchange_suffix

    def fetch(self) -> List[Symbol]:
        """CSV ファイルから銘柄リストを取得"""
        try:
            logger.info(f"Fetching symbols from CSV file: {self.file_path}")

            # CSV ファイルを読み込み
            df = pd.read_csv(self.file_path)
            logger.info(f"CSV columns: {df.columns.tolist()}, rows: {len(df)}")

            # 列のインデックスを取得
            if isinstance(self.symbol_col, int):
                if self.symbol_col >= len(df.columns):
                    raise ParseError(f"Symbol column index {self.symbol_col} out of range. Available columns: {df.columns.tolist()}")
                symbol_col_name = df.columns[self.symbol_col]
            else:
                symbol_col_name = self.symbol_col

            if isinstance(self.name_col, int):
                if self.name_col >= len(df.columns):
                    raise ParseError(f"Name column index {self.name_col} out of range. Available columns: {df.columns.tolist()}")
                name_col_name = df.columns[self.name_col]
            else:
                name_col_name = self.name_col

            logger.info(f"Using symbol column: '{symbol_col_name}', name column: '{name_col_name}'")

            # 必要な列を確認
            if symbol_col_name not in df.columns:
                raise ParseError(
                    f"Symbol column '{symbol_col_name}' not found. Available: {df.columns.tolist()}"
                )
            if name_col_name not in df.columns:
                raise ParseError(
                    f"Name column '{name_col_name}' not found. Available: {df.columns.tolist()}"
                )

            symbols = []
            invalid_count = 0
            for idx, row in df.iterrows():
                try:
                    raw_symbol = str(row[symbol_col_name])
                    symbol = self._normalize_symbol(raw_symbol)

                    # 日本株の自動検出と接尾辞追加
                    if self.auto_add_exchange_suffix:
                        symbol = self._add_exchange_suffix(symbol)

                    name = str(row[name_col_name])

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.debug(f"Invalid symbol at row {idx}: raw='{raw_symbol}', normalized='{symbol}'")
                        invalid_count += 1
                        continue

                    # 追加情報があれば取得
                    sector = ""
                    if "sector" in df.columns:
                        sector = str(row.get("sector", ""))

                    industry = ""
                    if "industry" in df.columns:
                        industry = str(row.get("industry", ""))

                    market = Market.OTHER
                    if "market" in df.columns:
                        market_str = str(row.get("market", "")).upper()
                        try:
                            market = Market(market_str)
                        except ValueError:
                            market = Market.OTHER

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=market,
                        sector=sector,
                        industry=industry,
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row {idx}: {e}")
                    continue

            if invalid_count > 0:
                logger.warning(f"Skipped {invalid_count} invalid symbols from CSV")

            logger.info(f"Successfully fetched {len(symbols)} symbols from CSV")
            return symbols

        except FileNotFoundError:
            raise DataSourceError(f"CSV file not found: {self.file_path}")
        except pd.errors.EmptyDataError:
            raise ParseError(f"CSV file is empty: {self.file_path}")
        except Exception as e:
            raise DataSourceError(f"Error reading CSV file: {e}")

    def _add_exchange_suffix(self, symbol: str) -> str:
        """取引所接尾辞を自動追加（日本株対応）"""
        # 既に接尾辞がある場合はそのまま返す
        if '.' in symbol:
            return symbol

        # 数字のみのシンボル = 日本株と判定
        if symbol.isdigit():
            # 4桁の数字 = 東京証券取引所
            if len(symbol) == 4:
                logger.debug(f"Adding .T suffix to Japanese stock: {symbol} -> {symbol}.T")
                return f"{symbol}.T"

        return symbol

    def is_available(self) -> bool:
        try:
            import os

            return os.path.exists(self.file_path)
        except:
            return False
