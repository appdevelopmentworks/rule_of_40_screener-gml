"""
Yahoo Finance データ取得クライアント
"""

import logging
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import yfinance as yf

try:
    from ..domain.models import DataFetchError, FinancialData
except ImportError:
    from src.core.domain.models import DataFetchError, FinancialData


logger = logging.getLogger(__name__)


class YFClient:
    """Yahoo Finance データ取得クライアント"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get_financial_data(self, symbol: str) -> FinancialData:
        """財務データを取得"""
        try:
            logger.debug(f"Fetching financial data for {symbol}")

            ticker = yf.Ticker(symbol)

            # Info データ取得
            info = ticker.info or {}

            # 財務諸表取得
            income_stmt = ticker.income_stmt
            ttm_income_stmt = ticker.ttm_income_stmt
            cashflow = ticker.cashflow

            financial_data = FinancialData(
                symbol=symbol,
                revenue_annual=(
                    income_stmt.loc["Total Revenue"]
                    if income_stmt is not None and "Total Revenue" in income_stmt.index
                    else None
                ),
                revenue_ttm=(
                    ttm_income_stmt.loc["Total Revenue"]
                    if ttm_income_stmt is not None and "Total Revenue" in ttm_income_stmt.index
                    else None
                ),
                operating_income_annual=(
                    income_stmt.loc["Operating Income"]
                    if income_stmt is not None and "Operating Income" in income_stmt.index
                    else None
                ),
                operating_income_ttm=(
                    ttm_income_stmt.loc["Operating Income"]
                    if ttm_income_stmt is not None and "Operating Income" in ttm_income_stmt.index
                    else None
                ),
                depreciation_annual=(
                    cashflow.loc["Depreciation & Amortization"]
                    if cashflow is not None and "Depreciation & Amortization" in cashflow.index
                    else None
                ),
                info=info,
                last_updated=datetime.now(),
            )

            # データ品質を評価
            financial_data.data_quality = self._evaluate_data_quality(financial_data)

            # デバッグ：取得したデータの内容をログ出力
            logger.debug(f"Data for {symbol}:")
            logger.debug(f"  Revenue TTM: {financial_data.revenue_ttm}")
            logger.debug(f"  Operating Income TTM: {financial_data.operating_income_ttm}")
            logger.debug(f"  Revenue Annual: {financial_data.revenue_annual}")
            logger.debug(f"  Operating Income Annual: {financial_data.operating_income_annual}")
            if financial_data.info:
                logger.debug(f"  Revenue Growth (info): {financial_data.info.get('revenueGrowth')}")
                logger.debug(f"  Operating Margins (info): {financial_data.info.get('operatingMargins')}")

            logger.debug(
                f"Successfully fetched data for {symbol}, quality: {financial_data.data_quality}"
            )
            return financial_data

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise DataFetchError(f"Failed to fetch data for {symbol}: {e}")

    def get_info_margins_growth(
        self, symbol: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """info から成長率とマージンを取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}

            revenue_growth = info.get("revenueGrowth")
            operating_margins = info.get("operatingMargins")

            return revenue_growth, operating_margins

        except Exception as e:
            logger.warning(f"Failed to get info margins for {symbol}: {e}")
            return None, None

    def get_income_statement(
        self, symbol: str, ttm: bool = False
    ) -> Optional[pd.DataFrame]:
        """損益計算書を取得"""
        try:
            ticker = yf.Ticker(symbol)

            if ttm:
                return ticker.ttm_income_stmt
            else:
                return ticker.income_stmt

        except Exception as e:
            logger.warning(f"Failed to get income statement for {symbol}: {e}")
            return None

    def get_cash_flow(self, symbol: str, ttm: bool = False) -> Optional[pd.DataFrame]:
        """キャッシュフロー計算書を取得"""
        try:
            ticker = yf.Ticker(symbol)

            if ttm:
                return ticker.ttm_cashflow
            else:
                return ticker.cashflow

        except Exception as e:
            logger.warning(f"Failed to get cash flow for {symbol}: {e}")
            return None

    def _evaluate_data_quality(self, data: FinancialData) -> str:
        """データ品質を評価"""
        from src.core.domain.models import DataQuality

        # 必須データのチェック
        has_revenue = (
            data.revenue_annual is not None and len(data.revenue_annual) > 0
        ) or (data.revenue_ttm is not None and len(data.revenue_ttm) > 0)

        has_operating_income = (
            data.operating_income_annual is not None
            and len(data.operating_income_annual) > 0
        ) or (
            data.operating_income_ttm is not None and len(data.operating_income_ttm) > 0
        )

        has_info = data.info is not None and len(data.info) > 0

        if has_revenue and has_operating_income and has_info:
            return DataQuality.COMPLETE.value
        elif has_revenue or has_operating_income:
            return DataQuality.PARTIAL.value
        else:
            return DataQuality.MISSING.value
