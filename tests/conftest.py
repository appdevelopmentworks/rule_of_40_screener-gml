"""
pytest 設定と共通フィクスチャ
"""

# プロジェクトルートを Python パスに追加
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.domain.models import (
        CalculationPeriod,
        DataQuality,
        FinancialData,
        Market,
        Rule40Result,
        Rule40Variant,
        Symbol,
    )
except ImportError:
    # テスト用のモック定義
    from dataclasses import dataclass
    from enum import Enum
    from typing import Optional

    class Market(Enum):
        NYSE = "NYSE"
        NASDAQ = "NASDAQ"
        AMEX = "AMEX"
        OTHER = "OTHER"

    class CalculationPeriod(Enum):
        ANNUAL = "annual"
        TTM = "ttm"
        MRQ_ANNUALIZED = "mrq_annualized"

    class Rule40Variant(Enum):
        OP = "op"
        EBITDA = "ebitda"
        BOTH = "both"

    class DataQuality(Enum):
        COMPLETE = "complete"
        PARTIAL = "partial"
        MISSING = "missing"

    @dataclass
    class Symbol:
        symbol: str
        name: str
        market: Market
        sector: str = ""
        industry: str = ""
        source: str = ""

    @dataclass
    class FinancialData:
        symbol: str
        revenue_annual: Optional[pd.Series] = None
        revenue_ttm: Optional[pd.Series] = None
        operating_income_annual: Optional[pd.Series] = None
        operating_income_ttm: Optional[pd.Series] = None
        depreciation_annual: Optional[pd.Series] = None
        depreciation_ttm: Optional[pd.Series] = None
        info: Optional[dict] = None
        last_updated: Optional[datetime] = None
        data_quality: DataQuality = DataQuality.MISSING

    @dataclass
    class Rule40Result:
        symbol: str
        name: str = ""
        r40_op: Optional[float] = None
        r40_ebitda: Optional[float] = None
        revenue_growth_yoy: Optional[float] = None
        operating_margin: Optional[float] = None
        ebitda_margin: Optional[float] = None
        period: CalculationPeriod = CalculationPeriod.TTM
        variant: Rule40Variant = Rule40Variant.OP
        calculation_time: datetime = None
        data_quality: DataQuality = DataQuality.MISSING


@pytest.fixture
def sample_symbol():
    """サンプル銘柄"""
    return Symbol(
        symbol="AAPL",
        name="Apple Inc.",
        market=Market.NASDAQ,
        sector="Technology",
        industry="Consumer Electronics",
        source="Test",
    )


@pytest.fixture
def sample_financial_data():
    """サンプル財務データ"""
    # 年次データ
    revenue_annual = pd.Series([394328, 365817, 365817], index=[2023, 2022, 2021])
    operating_income_annual = pd.Series(
        [114301, 119437, 108949], index=[2023, 2022, 2021]
    )
    depreciation_annual = pd.Series([11104, 9503, 8945], index=[2023, 2022, 2021])

    # TTM データ
    revenue_ttm = pd.Series([383285])
    operating_income_ttm = pd.Series([101234])
    depreciation_ttm = pd.Series([10500])

    return FinancialData(
        symbol="AAPL",
        revenue_annual=revenue_annual,
        revenue_ttm=revenue_ttm,
        operating_income_annual=operating_income_annual,
        operating_income_ttm=operating_income_ttm,
        depreciation_annual=depreciation_annual,
        depreciation_ttm=depreciation_ttm,
        info={
            "revenueGrowth": 0.078,
            "operatingMargins": 0.290,
            "marketCap": 3000000000000,
        },
        last_updated=datetime.now(),
        data_quality=DataQuality.COMPLETE,
    )


@pytest.fixture
def sample_symbols_list():
    """サンプル銘柄リスト"""
    return [
        Symbol(
            "AAPL", "Apple Inc.", Market.NASDAQ, "Technology", "Consumer Electronics"
        ),
        Symbol(
            "MSFT", "Microsoft Corporation", Market.NASDAQ, "Technology", "Software"
        ),
        Symbol(
            "GOOGL", "Alphabet Inc.", Market.NASDAQ, "Technology", "Internet Services"
        ),
        Symbol(
            "AMZN", "Amazon.com Inc.", Market.NASDAQ, "Consumer Cyclical", "E-Commerce"
        ),
        Symbol(
            "TSLA",
            "Tesla Inc.",
            Market.NASDAQ,
            "Consumer Cyclical",
            "Auto Manufacturers",
        ),
    ]


@pytest.fixture
def mock_config():
    """モック設定"""
    return {
        "ui": {
            "theme": "light",
            "locale": "ja",
            "window": {"width": 1200, "height": 800},
        },
        "fetch": {"max_workers": 4, "cache_ttl_hours": 24, "timeout_seconds": 30},
        "rule40": {"variant": "op", "period": "ttm", "threshold": 40.0},
        "cache": {"enabled": True, "database_path": "test_cache.db"},
    }


@pytest.fixture
def temp_db_file(tmp_path):
    """一時データベースファイル"""
    return tmp_path / "test_cache.db"


@pytest.fixture
def mock_yfinance_data():
    """yfinance モックデータ"""
    return {
        "info": {
            "revenueGrowth": 0.15,
            "operatingMargins": 0.25,
            "marketCap": 1000000000000,
            "symbol": "TEST",
        },
        "income_stmt": pd.DataFrame(
            {
                "Total Revenue": [100000, 90000, 80000],
                "Operating Income": [20000, 18000, 16000],
            },
            index=[2023, 2022, 2021],
        ),
        "ttm_income_stmt": pd.DataFrame(
            {"Total Revenue": [110000], "Operating Income": [22000]}, index=["TTM"]
        ),
        "cashflow": pd.DataFrame(
            {"Depreciation & Amortization": [5000, 4500, 4000]},
            index=[2023, 2022, 2021],
        ),
        "ttm_cashflow": pd.DataFrame(
            {"Depreciation & Amortization": [5500]}, index=["TTM"]
        ),
    }
