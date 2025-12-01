"""
日本取引所グループ (JPX) 上場銘柄取得アダプタ
"""

import logging
from typing import List

import pandas as pd
import requests

try:
    from ...domain.models import Market, Symbol
    from .base import BaseSymbolSource, DataSourceError, NetworkError, ParseError
except ImportError:
    from src.core.adapters.base import (
        BaseSymbolSource,
        DataSourceError,
        NetworkError,
        ParseError,
    )
    from src.core.domain.models import Market, Symbol


logger = logging.getLogger(__name__)


class JPXListedSource(BaseSymbolSource):
    """日本取引所グループ上場銘柄取得"""

    # JPXが公開している上場銘柄一覧のURL
    JPX_LISTED_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

    def __init__(self):
        super().__init__("JPX Listed (Tokyo Stock Exchange)")
        self.timeout = 30

    def fetch(self) -> List[Symbol]:
        """上場銘柄リストを取得"""
        try:
            logger.info(f"Fetching JPX listed companies from: {self.JPX_LISTED_URL}")

            # HTTPリクエスト
            response = requests.get(
                self.JPX_LISTED_URL,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )

            if response.status_code != 200:
                raise NetworkError(
                    f"Failed to fetch JPX data. Status code: {response.status_code}"
                )

            # Excelファイルをパース
            df = pd.read_excel(
                response.content,
                header=0,
                dtype={"コード": str},  # 証券コードを文字列として読み込む
            )

            logger.info(f"Loaded {len(df)} rows from JPX data")

            return self._parse_dataframe(df)

        except requests.RequestException as e:
            raise NetworkError(f"Network error while fetching JPX data: {e}")
        except Exception as e:
            raise DataSourceError(f"Error fetching JPX listed companies: {e}")

    def _parse_dataframe(self, df: pd.DataFrame) -> List[Symbol]:
        """DataFrameから銘柄リストを生成"""
        symbols = []

        # 必要な列を確認
        required_cols = ["コード", "銘柄名"]
        for col in required_cols:
            if col not in df.columns:
                raise ParseError(
                    f"Required column '{col}' not found. Available: {df.columns.tolist()}"
                )

        logger.info(f"DataFrame columns: {df.columns.tolist()}")

        invalid_count = 0
        for idx, row in df.iterrows():
            try:
                # 証券コードを取得（4桁の数字）
                code = str(row["コード"]).strip()

                # 無効なコードをスキップ
                if not code or code.lower() in ["nan", "none", ""]:
                    invalid_count += 1
                    continue

                # 数字のみかチェック
                if not code.isdigit():
                    logger.debug(f"Non-numeric code skipped: {code}")
                    invalid_count += 1
                    continue

                # 4桁のコードのみ対象（ETFなど5桁以上は除外）
                if len(code) != 4:
                    logger.debug(f"Non-4-digit code skipped: {code}")
                    invalid_count += 1
                    continue

                # Yahoo Finance用のシンボル（.T接尾辞追加）
                symbol = f"{code}.T"

                # 銘柄名
                name = str(row["銘柄名"]).strip()
                if name.lower() in ["nan", "none", ""]:
                    name = f"銘柄{code}"

                # 市場区分
                market = Market.OTHER
                if "市場・商品区分" in df.columns:
                    market_str = str(row.get("市場・商品区分", "")).strip()
                    if "プライム" in market_str:
                        market = Market.TSE_PRIME
                    elif "スタンダード" in market_str:
                        market = Market.TSE_STANDARD
                    elif "グロース" in market_str:
                        market = Market.TSE_GROWTH
                    else:
                        market = Market.OTHER

                # セクター（33業種区分）
                sector = ""
                if "33業種区分" in df.columns:
                    sector = str(row.get("33業種区分", "")).strip()
                    if sector.lower() in ["nan", "none", ""]:
                        sector = ""

                # 17業種区分も取得可能
                industry = ""
                if "17業種区分" in df.columns:
                    industry = str(row.get("17業種区分", "")).strip()
                    if industry.lower() in ["nan", "none", ""]:
                        industry = ""

                # Symbolオブジェクト作成
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
                invalid_count += 1
                continue

        if invalid_count > 0:
            logger.warning(f"Skipped {invalid_count} invalid entries")

        logger.info(
            f"Successfully parsed {len(symbols)} symbols from JPX listed data"
        )
        return symbols

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        try:
            response = requests.head(self.JPX_LISTED_URL, timeout=5)
            return response.status_code == 200
        except:
            return False
