"""
Wikipedia S&P 500 銘柄データ取得アダプタ
"""

import io
import logging
from typing import List

import pandas as pd
import requests

from src.core.adapters.base import (
    BaseSymbolSource,
    DataSourceError,
    NetworkError,
    ParseError,
)
from src.core.domain.models import Market, Symbol

logger = logging.getLogger(__name__)


class WikipediaSP500(BaseSymbolSource):
    """Wikipedia から S&P 500 銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Wikipedia S&P 500")
        self.url = url or "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    def fetch(self) -> List[Symbol]:
        """S&P 500 銘柄リストを取得"""
        try:
            logger.info(f"Fetching S&P 500 symbols from {self.url}")

            # User-Agent を設定してHTMLを取得
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            # pandas で HTML テーブルを読み込み（StringIOを使用）
            tables = pd.read_html(io.StringIO(response.text))

            if not tables:
                raise ParseError("No tables found on Wikipedia page")

            # 最初のテーブルが S&P 500 情報
            df = tables[0]

            # 必要な列を確認
            required_columns = ["Symbol", "Security"]
            if not all(col in df.columns for col in required_columns):
                raise ParseError(
                    f"Required columns not found. Available: {df.columns.tolist()}"
                )

            symbols = []
            for _, row in df.iterrows():
                try:
                    symbol = self._normalize_symbol(str(row["Symbol"]))
                    name = str(row["Security"])

                    # セクター情報があれば取得
                    sector = ""
                    if "GICS Sector" in df.columns:
                        sector = str(row.get("GICS Sector", ""))

                    # 業種情報があれば取得
                    industry = ""
                    if "GICS Sub-Industry" in df.columns:
                        industry = str(row.get("GICS Sub-Industry", ""))

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.warning(f"Invalid symbol: {symbol}")
                        continue

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=Market.OTHER,  # S&P 500 は複数市場にまたがる
                        sector=sector,
                        industry=industry,
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(f"Successfully fetched {len(symbols)} S&P 500 symbols")
            return symbols

        except requests.RequestException as e:
            raise NetworkError(f"Network error fetching Wikipedia page: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching S&P 500 data: {e}")

    def is_available(self) -> bool:
        """Wikipedia ページが利用可能かチェック"""
        try:
            # User-Agent を設定してボットとして扱われるのを回避
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Range': 'bytes=0-0'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            is_ok = response.status_code in [200, 206]  # 206 for partial content
            if not is_ok:
                logger.warning(f"Wikipedia SP500 availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.warning(f"Wikipedia SP500 availability check error: {e}")
            return False


class WikipediaSP400(BaseSymbolSource):
    """Wikipedia から S&P 400 銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Wikipedia S&P 400")
        self.url = url or "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"

    def fetch(self) -> List[Symbol]:
        """S&P 400 銘柄リストを取得"""
        try:
            logger.info(f"Fetching S&P 400 symbols from {self.url}")

            # User-Agent を設定してHTMLを取得
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            # pandas で HTML テーブルを読み込み（StringIOを使用）
            tables = pd.read_html(io.StringIO(response.text))

            if not tables:
                raise ParseError("No tables found on Wikipedia page")

            df = tables[0]

            # 必要な列を確認
            required_columns = ["Symbol", "Security"]
            if not all(col in df.columns for col in required_columns):
                raise ParseError(
                    f"Required columns not found. Available: {df.columns.tolist()}"
                )

            symbols = []
            for _, row in df.iterrows():
                try:
                    symbol = self._normalize_symbol(str(row["Symbol"]))
                    name = str(row["Security"])

                    sector = ""
                    if "GICS Sector" in df.columns:
                        sector = str(row.get("GICS Sector", ""))

                    industry = ""
                    if "GICS Sub-Industry" in df.columns:
                        industry = str(row.get("GICS Sub-Industry", ""))

                    if not self._validate_symbol(symbol):
                        logger.warning(f"Invalid symbol: {symbol}")
                        continue

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=Market.OTHER,
                        sector=sector,
                        industry=industry,
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(f"Successfully fetched {len(symbols)} S&P 400 symbols")
            return symbols

        except requests.RequestException as e:
            raise NetworkError(f"Network error fetching Wikipedia page: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching S&P 400 data: {e}")

    def is_available(self) -> bool:
        """Wikipedia ページが利用可能かチェック"""
        try:
            # User-Agent を設定してボットとして扱われるのを回避
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Range': 'bytes=0-0'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            is_ok = response.status_code in [200, 206]  # 206 for partial content
            if not is_ok:
                logger.warning(f"Wikipedia SP400 availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.warning(f"Wikipedia SP400 availability check error: {e}")
            return False
