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


class NasdaqListed(BaseSymbolSource):
    """Nasdaq 上場銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Nasdaq Listed")
        self.url = url or "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"

    def fetch(self) -> List[Symbol]:
        """Nasdaq 上場銘柄リストを取得"""
        try:
            logger.info(f"Fetching Nasdaq listed symbols from {self.url}")

            # HTTP 経由で取得（FTP の代わり）
            http_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(http_url, headers=headers, timeout=30)
            response.raise_for_status()

            # テキストデータをパース
            text_data = response.text

            # pandas で読み込み（タブ区切り）
            df = pd.read_csv(io.StringIO(text_data), sep="|")

            # 最終行の "File Creation Time" を除去
            if "File Creation Time" in df.iloc[-1].values[0]:
                df = df.iloc[:-1]

            symbols = []
            for _, row in df.iterrows():
                try:
                    symbol = self._normalize_symbol(str(row["Symbol"]))
                    name = str(row["Security Name"])

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.warning(f"Invalid symbol: {symbol}")
                        continue

                    # Test Issue などは除外
                    test_issue = row.get("Test Issue")
                    if test_issue and str(test_issue).strip().upper() == "Y":
                        continue

                    symbol_obj = Symbol(
                        symbol=symbol,
                        name=name,
                        market=Market.NASDAQ,
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
            http_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(http_url, headers=headers, timeout=10)
            is_ok = response.status_code == 200
            if not is_ok:
                logger.warning(f"Nasdaq availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.warning(f"Nasdaq availability check error: {e}")
            return False


class OtherListed(BaseSymbolSource):
    """Nasdaq 以外の上場銘柄を取得"""

    def __init__(self, url: str | None = None):
        super().__init__("Other Listed")
        self.url = url or "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"

    def fetch(self) -> List[Symbol]:
        """Nasdaq 以外の上場銘柄リストを取得"""
        try:
            logger.info(f"Fetching other listed symbols from {self.url}")

            # HTTP 経由で取得
            http_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(http_url, headers=headers, timeout=30)
            response.raise_for_status()

            text_data = response.text

            # pandas で読み込み（タブ区切り）
            df = pd.read_csv(io.StringIO(text_data), sep="|")

            # 最終行の "File Creation Time" を除去
            if "File Creation Time" in df.iloc[-1].values[0]:
                df = df.iloc[:-1]

            symbols = []
            for _, row in df.iterrows():
                try:
                    symbol = self._normalize_symbol(str(row["ACT Symbol"]))
                    name = str(row["Security Name"])

                    # バリデーション
                    if not self._validate_symbol(symbol):
                        logger.warning(f"Invalid symbol: {symbol}")
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
            http_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(http_url, headers=headers, timeout=10)
            is_ok = response.status_code == 200
            if not is_ok:
                logger.warning(f"Other listed availability check failed: status={response.status_code}")
            return is_ok
        except Exception as e:
            logger.warning(f"Other listed availability check error: {e}")
            return False
