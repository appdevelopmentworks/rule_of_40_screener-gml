"""
日経500 銘柄取得アダプタ
"""

import logging
import re
from typing import List

import cloudscraper
from bs4 import BeautifulSoup

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


class Nikkei500Source(BaseSymbolSource):
    """日経500 銘柄取得"""

    # 日経インデックスの日経500構成銘柄ページ
    NIKKEI500_URL = "https://indexes.nikkei.co.jp/nkave/index/component?idx=nk500av"

    # 業種セクター定義
    SECTORS = {
        "水産", "鉱業", "建設", "食品", "繊維", "パルプ・紙", "化学", "医薬品", "石油", "ゴム", "窯業",
        "鉄鋼", "非鉄・金属", "機械", "電気機器", "造船", "自動車", "輸送用機器", "精密機器", "その他製造",
        "商社", "小売業", "銀行", "その他金融", "証券", "保険", "不動産", "鉄道・バス", "陸運", "海運",
        "空運", "通信", "倉庫", "電力", "ガス", "サービス"
    }

    def __init__(self):
        super().__init__("Nikkei 500")
        self.timeout = 30

    def fetch(self) -> List[Symbol]:
        """日経500銘柄リストを取得"""
        try:
            logger.info(f"Fetching Nikkei 500 companies from: {self.NIKKEI500_URL}")

            # Cloudflare対策のためcloudscraperを使用
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )

            # HTTPリクエスト
            headers = {
                "Referer": "https://indexes.nikkei.co.jp/",
                "Accept-Language": "ja,en;q=0.9",
            }

            response = scraper.get(
                self.NIKKEI500_URL,
                timeout=self.timeout,
                headers=headers,
            )

            if response.status_code != 200:
                logger.error(f"HTTP error: status code {response.status_code}")
                logger.error(f"Response content (first 500 chars): {response.text[:500]}")
                raise NetworkError(
                    f"Failed to fetch Nikkei 500 data. Status code: {response.status_code}"
                )

            logger.info(f"Successfully fetched HTML ({len(response.text)} bytes)")

            return self._parse_html(response.text)

        except ParseError as e:
            logger.error(f"Parse error: {e}")
            raise
        except NetworkError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)
            raise DataSourceError(f"Error fetching Nikkei 500 companies: {e}")

    def _parse_html(self, html: str) -> List[Symbol]:
        """HTMLから銘柄リストをパース"""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # 1) 旧レイアウト（table）対応：もし残っていればそのまま使う
        tables = soup.select("div.idx-index-components table")
        if tables:
            for tbl in tables:
                sector_el = tbl.find_previous("h3")
                sector = sector_el.get_text(strip=True) if sector_el else ""
                for tr in tbl.select("tbody tr"):
                    tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if len(tds) >= 3 and re.fullmatch(r"\d{4}", tds[0]):
                        code, brand, company = tds[0], tds[1], tds[2]
                        results.append([code, brand, company, sector])
            if results:
                logger.info(f"Parsed {len(results)} stocks from table layout")
                return self._convert_to_symbols(results)

        # 2) 新レイアウト（業種h3＋羅列）対応
        for h3 in soup.find_all("h3"):
            sector = h3.get_text(strip=True)
            if sector not in self.SECTORS:
                continue

            block_nodes = []
            for sib in h3.next_siblings:
                # 次の業種見出しでブロックを終了
                if getattr(sib, "name", None) == "h3":
                    break
                block_nodes.append(sib)

            # ブロック内テキストを行に分解
            text = " ".join(
                n.get_text(" ", strip=True) if hasattr(n, "get_text") else str(n).strip()
                for n in block_nodes
            )
            # 「コード 銘柄名 社名」形式を緩めに抽出
            for m in re.finditer(
                r"(?P<code>\d{4})\s+(?P<brand>[^\s【]+)\s+(?P<company>[^#\s][^0-9]{1,40})",
                text,
            ):
                code = m.group("code")
                brand = m.group("brand").strip()
                company = m.group("company").strip()
                # 会社名のノイズ削減
                company = re.sub(r"[【】]|www\.nikkei\.com", "", company).strip()
                results.append([code, brand, company, sector])

        if not results:
            raise ParseError("No stock data found in HTML")

        # 重複除去
        uniq = {}
        for code, brand, company, sector in results:
            uniq[(code, brand, company)] = sector
        unique_results = [[c, b, k, s] for (c, b, k), s in uniq.items()]

        logger.info(f"Parsed {len(unique_results)} unique stocks from new layout")
        return self._convert_to_symbols(unique_results)

    def _convert_to_symbols(self, data: List[List[str]]) -> List[Symbol]:
        """パースした銘柄データをSymbolオブジェクトに変換"""
        symbols = []
        invalid_count = 0

        for row in data:
            try:
                code, brand, company, sector = row

                # 4桁の数字コードのみ対象
                if not re.fullmatch(r"\d{4}", code):
                    logger.debug(f"Invalid code format skipped: {code}")
                    invalid_count += 1
                    continue

                # Yahoo Finance用のシンボル（.T接尾辞追加）
                symbol = f"{code}.T"

                # 銘柄名（ブランド名を優先、なければ社名）
                name = brand if brand else company
                if not name:
                    name = f"銘柄{code}"

                # 日経500は主に東証プライム市場
                market = Market.TSE_PRIME

                # Symbolオブジェクト作成
                symbol_obj = Symbol(
                    symbol=symbol,
                    name=name,
                    market=market,
                    sector=sector,
                    industry="",
                    source=self.get_source_name(),
                )

                symbols.append(symbol_obj)

            except Exception as e:
                logger.warning(f"Error processing row {row}: {e}")
                invalid_count += 1
                continue

        if invalid_count > 0:
            logger.warning(f"Skipped {invalid_count} invalid entries")

        logger.info(
            f"Successfully converted {len(symbols)} symbols from Nikkei 500 data"
        )
        return symbols

    def is_available(self) -> bool:
        """データソースが利用可能かチェック

        Note: 日経のサイトはアクセスチェックでも403を返すことがあるため、
        常にTrueを返して実際のfetch時にエラーハンドリングを行う
        """
        # 常に利用可能として扱い、実際のfetch時にエラーを処理
        logger.debug("Nikkei500Source is_available check - returning True (will check on fetch)")
        return True
