"""
Nasdaq 銘柄リスト取得アダプタ
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
)
from src.core.domain.models import Market, Symbol

logger = logging.getLogger(__name__)


class Nasdaq100(BaseSymbolSource):
    """Nasdaq 100 銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Nasdaq 100")
        self.url = url or "https://en.wikipedia.org/wiki/Nasdaq-100"

    def fetch(self) -> List[Symbol]:
        """Nasdaq 100 銘柄リストを取得"""
        try:
            logger.info(f"Fetching Nasdaq 100 symbols from {self.url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            # HTML テーブルをパース
            tables = pd.read_html(response.text)

            # Nasdaq-100 のテーブルを探す（通常4番目のテーブル）
            df = None
            for i, table in enumerate(tables):
                if 'Ticker' in table.columns or 'Symbol' in table.columns:
                    # Company列も含むテーブルを探す
                    if 'Company' in table.columns or 'Security' in table.columns:
                        df = table
                        logger.info(f"Found Nasdaq-100 table at index {i}")
                        break

            if df is None:
                # フォールバック: 4番目のテーブルを使用
                if len(tables) > 4:
                    df = tables[4]
                else:
                    raise ParseError("Could not find Nasdaq-100 table")

            logger.info(f"Found {len(df)} rows with columns: {df.columns.tolist()}")

            symbols = []
            for _, row in df.iterrows():
                try:
                    # Ticker または Symbol 列を取得
                    if "Ticker" in df.columns:
                        symbol = self._normalize_symbol(str(row["Ticker"]))
                    elif "Symbol" in df.columns:
                        symbol = self._normalize_symbol(str(row["Symbol"]))
                    else:
                        symbol = self._normalize_symbol(str(row.iloc[0]))

                    # Company または Security 列を取得
                    if "Company" in df.columns:
                        name = str(row["Company"])
                    elif "Security" in df.columns:
                        name = str(row["Security"])
                    else:
                        name = str(row.iloc[1]) if len(row) > 1 else symbol

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.debug(f"Invalid symbol: {symbol}")
                        continue

                    # GICS Sector情報
                    sector = ""
                    if "GICS Sector" in df.columns:
                        sector = str(row.get("GICS Sector", ""))

                    # GICS Sub-Industry情報
                    industry = ""
                    if "GICS Sub-Industry" in df.columns:
                        industry = str(row.get("GICS Sub-Industry", ""))

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=Market.NASDAQ,
                        sector=sector,
                        industry=industry,
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(f"Successfully fetched {len(symbols)} Nasdaq 100 symbols")
            return symbols

        except requests.RequestException as e:
            raise NetworkError(f"Network error fetching Nasdaq 100 data: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching Nasdaq 100 data: {e}")

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(self.url, headers=headers, timeout=10)
            is_ok = response.status_code == 200
            if not is_ok:
                logger.warning(f"Nasdaq 100 availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.debug(f"Nasdaq 100 availability check error: {e}")
            return False


class NasdaqListed(BaseSymbolSource):
    """Nasdaq 上場銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Nasdaq Listed")
        # www.nasdaqtrader.comからテキストファイルを取得
        self.url = url or "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"

    def fetch(self) -> List[Symbol]:
        """Nasdaq 上場銘柄リストを取得"""
        try:
            logger.info(f"Fetching Nasdaq listed symbols from {self.url}")

            # HTTPSで取得
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            # テキストデータをパース（パイプ区切り）
            text_data = response.text
            df = pd.read_csv(io.StringIO(text_data), sep="|")

            # 最終行の "File Creation Time" を除去
            if len(df) > 0 and "File Creation Time" in str(df.iloc[-1].values[0]):
                df = df.iloc[:-1]

            logger.info(f"Found {len(df)} rows with columns: {df.columns.tolist()}")

            symbols = []
            for _, row in df.iterrows():
                try:
                    # Symbol列を取得
                    symbol = self._normalize_symbol(str(row["Symbol"]))
                    name = str(row["Security Name"])

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.debug(f"Invalid symbol: {symbol}")
                        continue

                    # Test Issue は除外
                    test_issue = row.get("Test Issue")
                    if test_issue and str(test_issue).strip().upper() == "Y":
                        continue

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=Market.NASDAQ,
                        sector="",
                        industry="",
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(f"Successfully fetched {len(symbols)} Nasdaq listed symbols")
            return symbols

        except requests.RequestException as e:
            raise NetworkError(f"Network error fetching Nasdaq data: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching Nasdaq listed data: {e}")

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Range': 'bytes=0-0'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            is_ok = response.status_code in [200, 206]
            if not is_ok:
                logger.warning(f"Nasdaq availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.debug(f"Nasdaq availability check error: {e}")
            return False


class OtherListed(BaseSymbolSource):
    """Nasdaq 以外の上場銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Other Listed")
        self.url = url or "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"

    def fetch(self) -> List[Symbol]:
        """Nasdaq 以外の上場銘柄リストを取得"""
        try:
            logger.info(f"Fetching other listed symbols from {self.url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            text_data = response.text

            # pandas で読み込み（パイプ区切り）
            df = pd.read_csv(io.StringIO(text_data), sep="|")

            # 最終行の "File Creation Time" を除去
            if len(df) > 0 and "File Creation Time" in str(df.iloc[-1].values[0]):
                df = df.iloc[:-1]

            symbols = []
            for _, row in df.iterrows():
                try:
                    symbol = self._normalize_symbol(str(row["ACT Symbol"]))
                    name = str(row["Security Name"])

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.debug(f"Invalid symbol: {symbol}")
                        continue

                    # Test Issue などは除外
                    test_issue = row.get("Test Issue")
                    if test_issue and str(test_issue).strip().upper() == "Y":
                        continue

                    # Exchange から市場を判定
                    exchange = str(row.get("Exchange", "")).strip()
                    market = self._determine_market(exchange)

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=market,
                        source=self.get_source_name(),
                    )

                    symbols.append(symbol_obj)

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    continue

            logger.info(f"Successfully fetched {len(symbols)} other listed symbols")
            return symbols

        except requests.RequestException as e:
            raise NetworkError(f"Network error fetching other listed data: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching other listed data: {e}")

    def _determine_market(self, exchange: str) -> Market:
        """Exchange コードから市場を判定"""
        exchange_map = {
            "N": Market.NYSE,
            "A": Market.AMEX,
            "P": Market.NASDAQ,  # ARCA
            "Z": Market.NASDAQ,  # BATS
            "V": Market.NASDAQ,  # IEX
        }

        return exchange_map.get(exchange.upper(), Market.OTHER)

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Range': 'bytes=0-0'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            is_ok = response.status_code in [200, 206]
            if not is_ok:
                logger.warning(f"Other listed availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.debug(f"Other listed availability check error: {e}")
            return False
