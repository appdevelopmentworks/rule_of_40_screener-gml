"""
スクリーニングサービス
"""

import concurrent.futures
import logging
from datetime import datetime
from typing import List, Optional

try:
    from ..adapters.csv_source import CSVFileSource
    from ..adapters.nasdaq_txt import NasdaqListed, OtherListed
    from ..adapters.wikipedia_sp500 import WikipediaSP400, WikipediaSP500
    from ..data.cache import CacheManager
    from ..data.config_loader import ConfigManager
    from ..data.yf_client import YFClient
    from ..domain.models import (
        CalculationError,
        DataFetchError,
        FinancialData,
        Rule40Result,
        ScreeningConfig,
        Symbol,
    )
    from ..domain.rule40 import Rule40Calculator
except ImportError:
    from src.core.adapters.csv_source import CSVFileSource
    from src.core.adapters.nasdaq_txt import NasdaqListed, OtherListed
    from src.core.adapters.wikipedia_sp500 import WikipediaSP400, WikipediaSP500
    from src.core.data.cache import CacheManager
    from src.core.data.config_loader import ConfigManager
    from src.core.data.yf_client import YFClient
    from src.core.domain.models import (
        CalculationError,
        DataFetchError,
        FinancialData,
        Rule40Result,
        ScreeningConfig,
        Symbol,
    )
    from src.core.domain.rule40 import Rule40Calculator

logger = logging.getLogger(__name__)


class ScreeningService:
    """スクリーニングサービス"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.calculator = Rule40Calculator()
        self.yf_client = YFClient()

        # キャッシュ設定
        cache_path = config_manager.get("cache.path", "src/app_data/cache/screening.db")
        cache_ttl = config_manager.get("cache.ttl_hours", 24)
        self.cache = CacheManager(cache_path, cache_ttl)

        # データソース初期化
        self._init_data_sources()

    def _init_data_sources(self):
        """データソース初期化"""
        self.data_sources = {
            "sp500": WikipediaSP500(),
            "sp400": WikipediaSP400(),
            "nasdaq": NasdaqListed(),
            "other": OtherListed(),
        }

    def screen_stocks(
        self, config: ScreeningConfig, progress_callback=None, result_callback=None
    ) -> List[Rule40Result]:
        """株式スクリーニング実行"""
        try:
            # 設定の検証と修正
            max_workers = max(1, config.max_workers)
            if config.max_workers <= 0:
                logger.warning("max_workers was <= 0, setting to 1")
            
            logger.info(f"Starting screening with config: {config}")
            start_time = datetime.now()

            # 1. 銘柄リスト取得
            if progress_callback:
                progress_callback(0, 4, "銘柄リストを取得中...")

            symbols = self._get_symbols(config)
            logger.info(f"Found {len(symbols)} symbols to screen")

            # 2. 財務データ取得
            if progress_callback:
                progress_callback(1, 4, f"財務データを取得中 ({len(symbols)}銘柄)...")

            financial_data_list = self._fetch_financial_data(
                symbols, config, progress_callback, result_callback
            )
            logger.info(
                f"Successfully fetched data for {len(financial_data_list)} symbols"
            )

            # 3. Rule of 40 計算
            if progress_callback:
                progress_callback(2, 4, "Rule of 40を計算中...")

            results = self._calculate_rule40(
                financial_data_list, config, progress_callback, result_callback
            )
            logger.info(f"Calculated Rule of 40 for {len(results)} symbols")

            # 4. フィルタリング
            if progress_callback:
                progress_callback(3, 4, "結果をフィルタリング中...")

            filtered_results = self._apply_filters(results, config)
            logger.info(f"After filtering: {len(filtered_results)} symbols")

            # 5. ソート
            sorted_results = self._sort_results(filtered_results, config)

            # 6. 追加情報付与
            if progress_callback:
                progress_callback(4, 4, "最終処理中...")

            enriched_results = self._enrich_results(sorted_results)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Screening completed in {elapsed:.1f} seconds")

            return enriched_results

        except Exception as e:
            logger.error(f"Screening failed: {e}")
            raise

    def _get_symbols(self, config: ScreeningConfig) -> List[Symbol]:
        """銘柄リスト取得"""
        all_symbols = []

        for source_name in config.sources:
            if source_name in self.data_sources:
                try:
                    source = self.data_sources[source_name]
                    if source.is_available():
                        symbols = source.fetch()
                        all_symbols.extend(symbols)
                        logger.info(f"Got {len(symbols)} symbols from {source_name}")
                    else:
                        logger.warning(f"Data source {source_name} is not available")
                except Exception as e:
                    logger.error(f"Failed to fetch symbols from {source_name}: {e}")

        # CSVファイルから取得
        if config.csv_path:
            try:
                # 1列目をsymbol列として、name列はsymbolと同じに設定
                csv_source = CSVFileSource(config.csv_path, symbol_col=0, name_col=0)
                if csv_source.is_available():
                    csv_symbols = csv_source.fetch()
                    all_symbols.extend(csv_symbols)
                    logger.info(f"Got {len(csv_symbols)} symbols from CSV")
            except Exception as e:
                logger.error(f"Failed to fetch symbols from CSV: {e}")

        # 除外銘柄をフィルター
        if config.exclude_symbols:
            exclude_set = set(config.exclude_symbols)
            all_symbols = [s for s in all_symbols if s.symbol not in exclude_set]
            logger.info(f"Excluded {len(config.exclude_symbols)} symbols")

        # 重複除去（後勝ち）
        unique_symbols = {}
        for symbol in all_symbols:
            unique_symbols[symbol.symbol] = symbol

        return list(unique_symbols.values())

    def _fetch_financial_data(
        self,
        symbols: List[Symbol],
        config: ScreeningConfig,
        progress_callback=None,
        result_callback=None,
    ) -> List[FinancialData]:
        """財務データ取得"""
        financial_data_list = []

        # シンボルが0の場合は早期リターン
        if len(symbols) == 0:
            return financial_data_list

        # 並列処理（レート制限対策）
        max_workers = min(max(1, config.max_workers), len(symbols), 2)  # 最大2並列に制限

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # タスク送信
            future_to_symbol = {
                executor.submit(
                    self._fetch_single_financial_data, symbol, config
                ): symbol
                for symbol in symbols
            }

            # 結果収集
            completed_count = 0
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data:
                        financial_data_list.append(data)
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol.symbol}: {e}")

                completed_count += 1
                if progress_callback:
                    progress = completed_count / len(symbols)
                    progress_callback(
                        int(progress * 100),
                        100,
                        f"財務データ取得中: {completed_count}/{len(symbols)} ({symbol.symbol})",
                    )

        return financial_data_list

    def _fetch_single_financial_data(
        self, symbol: Symbol, config: ScreeningConfig
    ) -> Optional[FinancialData]:
        """単一銘柄の財務データ取得"""
        # キャッシュキー
        cache_key = f"financial_data_{symbol.symbol}"

        # キャッシュから取得（強制更新でない場合）
        if not config.force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.debug(f"Using cached data for {symbol.symbol}")
                return FinancialData(**cached_data)

        try:
            # レート制限対策：リクエスト前に遅延
            import time
            import random
            time.sleep(random.uniform(0.5, 1.5))  # 0.5-1.5秒のランダム遅延

            # リトライ機能付きでデータ取得
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    data = self.yf_client.get_financial_data(symbol.symbol)
                    break
                except Exception as e:
                    if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 5  # 5秒, 10秒, 15秒
                            logger.warning(f"Rate limited for {symbol.symbol}, waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                    raise

            # キャッシュに保存
            self.cache.set(cache_key, data.__dict__, config.cache_ttl_hours)

            return data

        except DataFetchError as e:
            logger.warning(f"Failed to fetch data for {symbol.symbol}: {e}")
            return None

    def _calculate_rule40(
        self,
        financial_data_list: List[FinancialData],
        config: ScreeningConfig,
        progress_callback=None,
        result_callback=None,
    ) -> List[Rule40Result]:
        """Rule of 40 計算"""
        results = []

        for i, data in enumerate(financial_data_list):
            try:
                result = self.calculator.calculate(
                    data, period=config.period, variant=config.variant
                )

                # 基本情報設定
                if data.info:
                    result.name = data.info.get(
                        "longName", data.info.get("shortName", "")
                    )
                    result.market_cap = data.info.get("marketCap")
                    result.sector = data.info.get("sector", "")
                    result.industry = data.info.get("industry", "")

                results.append(result)

                # 個別結果コールバック
                if result_callback:
                    result_callback(result)

            except CalculationError as e:
                logger.warning(f"Failed to calculate Rule of 40 for {data.symbol}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error calculating for {data.symbol}: {e}")

            # プログレス更新
            if progress_callback:
                progress = (i + 1) / len(financial_data_list)
                progress_callback(
                    int(progress * 100),
                    100,
                    f"Rule of 40計算中: {i + 1}/{len(financial_data_list)} ({data.symbol})",
                )

        return results

    def _apply_filters(
        self, results: List[Rule40Result], config: ScreeningConfig
    ) -> List[Rule40Result]:
        """フィルター適用"""
        filtered = results

        # Rule of 40 閾値フィルター
        if config.threshold is not None:
            filtered = [
                r
                for r in filtered
                if r.meets_threshold(config.threshold, config.variant)
            ]
            logger.debug(f"After threshold filter ({config.threshold}): {len(filtered)} symbols")

        # 最小売上高フィルター
        if config.min_revenue:
            filtered = [
                r
                for r in filtered
                if r.market_cap and r.market_cap >= config.min_revenue
            ]

        # 黒字のみフィルター
        if config.margin_positive_only:
            filtered = [
                r
                for r in filtered
                if (r.operating_margin and r.operating_margin > 0)
                or (r.ebitda_margin and r.ebitda_margin > 0)
            ]

        # カスタムフィルター
        for filter_obj in config.filters:
            filtered = [r for r in filtered if filter_obj.apply(r)]
            logger.debug(f"After filter {filter_obj.field} {filter_obj.operator} {filter_obj.value}: {len(filtered)} symbols")

        return filtered

    def _sort_results(
        self, results: List[Rule40Result], config: ScreeningConfig
    ) -> List[Rule40Result]:
        """結果ソート"""
        if config.sort_config:
            return sorted(
                results,
                key=config.sort_config.get_key,
                reverse=not config.sort_config.ascending,
            )
        else:
            # デフォルト：Rule of 40の降順
            return sorted(
                results,
                key=lambda r: r.get_r40_value(config.variant) or float("-inf"),
                reverse=True,
            )

    def _enrich_results(self, results: List[Rule40Result]) -> List[Rule40Result]:
        """結果に追加情報を付与"""
        # TODO: 追加情報の付与処理
        return results

    def get_cache_stats(self) -> dict:
        """キャッシュ統計取得"""
        return self.cache.get_stats()

    def clear_cache(self):
        """キャッシュクリア"""
        self.cache.clear_all()
        logger.info("Cache cleared")

    def cleanup_cache(self) -> int:
        """キャッシュクリーンアップ"""
        return self.cache.cleanup()
