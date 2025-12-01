"""
Domain models for financial data and screening results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd


class CalculationPeriod(Enum):
    """計算期間"""

    ANNUAL = "annual"
    TTM = "ttm"
    MRQ_ANNUALIZED = "mrq_annualized"


class Rule40Variant(Enum):
    """Rule of 40 計算バリアント"""

    OP = "op"  # 営業利益版
    EBITDA = "ebitda"  # EBITDA版
    BOTH = "both"  # 両方


class DataQuality(Enum):
    """データ品質"""

    COMPLETE = "complete"  # 完全
    PARTIAL = "partial"  # 部分的
    MISSING = "missing"  # 欠損


class Market(Enum):
    """市場"""

    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    AMEX = "AMEX"
    JPX = "JPX"  # 日本取引所
    TSE_PRIME = "TSE_PRIME"  # 東証プライム
    TSE_STANDARD = "TSE_STANDARD"  # 東証スタンダード
    TSE_GROWTH = "TSE_GROWTH"  # 東証グロース
    OTHER = "OTHER"


@dataclass
class Symbol:
    """銘柄情報"""

    symbol: str
    name: str
    market: Market
    sector: str = ""
    industry: str = ""
    source: str = ""

    def __post_init__(self):
        if isinstance(self.market, str):
            self.market = Market(self.market)


@dataclass
class FinancialData:
    """財務データ"""

    symbol: str

    # 売上データ
    revenue_annual: Optional[pd.Series] = None
    revenue_ttm: Optional[pd.Series] = None
    revenue_mrq: Optional[pd.Series] = None

    # 営業利益データ
    operating_income_annual: Optional[pd.Series] = None
    operating_income_ttm: Optional[pd.Series] = None
    operating_income_mrq: Optional[pd.Series] = None

    # 減価償却費データ
    depreciation_annual: Optional[pd.Series] = None
    depreciation_ttm: Optional[pd.Series] = None
    depreciation_mrq: Optional[pd.Series] = None

    # Yahoo Finance info データ
    info: Optional[Dict[str, Any]] = None

    # メタデータ
    last_updated: Optional[datetime] = None
    data_quality: DataQuality = DataQuality.MISSING

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class Rule40Result:
    """Rule of 40 計算結果"""

    symbol: str
    name: str = ""

    # 計算結果
    r40_op: Optional[float] = None  # 営業利益版
    r40_ebitda: Optional[float] = None  # EBITDA版

    # 構成要素
    revenue_growth_yoy: Optional[float] = None
    operating_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None

    # メタデータ
    period: CalculationPeriod = CalculationPeriod.TTM
    variant: Rule40Variant = Rule40Variant.OP
    calculation_time: datetime = field(default_factory=datetime.now)
    data_quality: DataQuality = DataQuality.MISSING

    # 追加情報
    market_cap: Optional[float] = None
    sector: str = ""
    industry: str = ""

    def get_r40_value(self, variant: Optional[Rule40Variant] = None) -> Optional[float]:
        """指定バリアントのR40値を取得"""
        if variant is None:
            variant = self.variant

        if variant == Rule40Variant.OP:
            return self.r40_op
        elif variant == Rule40Variant.EBITDA:
            return self.r40_ebitda
        elif variant == Rule40Variant.BOTH:
            return self.r40_op if self.r40_op is not None else self.r40_ebitda

        return None

    def meets_threshold(
        self, threshold: float = 40.0, variant: Optional[Rule40Variant] = None
    ) -> bool:
        """閾値を満たすかチェック"""
        r40_value = self.get_r40_value(variant)
        return r40_value is not None and r40_value >= threshold


@dataclass
class Filter:
    """フィルタ条件"""

    field: str  # r40_op, r40_ebitda, revenue_growth, etc.
    operator: str  # gt, gte, lt, lte, eq, neq, contains
    value: Any

    def apply(self, result: Rule40Result) -> bool:
        """フィルタを適用"""
        # フィールド値を取得
        field_value = getattr(result, self.field, None)

        if field_value is None:
            return False

        # 演算子に応じて比較
        if self.operator == "gt":
            return field_value > self.value
        elif self.operator == "gte":
            return field_value >= self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "lte":
            return field_value <= self.value
        elif self.operator == "eq":
            return field_value == self.value
        elif self.operator == "neq":
            return field_value != self.value
        elif self.operator == "contains":
            return str(self.value).lower() in str(field_value).lower()

        return False


@dataclass
class SortConfig:
    """ソート設定"""

    field: str
    ascending: bool = False

    def get_key(self, result: Rule40Result) -> Any:
        """ソートキーを取得"""
        value = getattr(result, self.field, None)

        # None 値の処理
        if value is None:
            return float("-inf") if not self.ascending else float("inf")

        return value


@dataclass
class ScreeningConfig:
    """スクリーニング設定"""

    # ユニバース設定
    sources: List[str] = field(
        default_factory=lambda: ["sp500", "sp400", "nasdaq", "other"]
    )
    csv_path: Optional[str] = None
    exclude_symbols: List[str] = field(default_factory=list)

    # Rule of 40 設定
    variant: Rule40Variant = Rule40Variant.OP
    period: CalculationPeriod = CalculationPeriod.TTM
    threshold: float = 40.0

    # フィルタ設定
    filters: List[Filter] = field(default_factory=list)

    # ソート設定
    sort_config: Optional[SortConfig] = None

    # データ取得設定
    max_workers: int = 12
    cache_ttl_hours: int = 24
    force_refresh: bool = False

    # 最小条件
    min_revenue: Optional[float] = None
    margin_positive_only: bool = False


@dataclass
class CacheEntry:
    """キャッシュエントリ"""

    key: str
    value: Any
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        """期限切れチェック"""
        return datetime.now() > self.expires_at


@dataclass
class ExportConfig:
    """エクスポート設定"""

    format: str = "csv"  # csv, xlsx
    encoding: str = "utf-8"
    include_metadata: bool = True
    decimal_places: int = 2
    file_path: Optional[str] = None

    # CSV固有設定
    csv_delimiter: str = ","

    # Excel固有設定
    excel_sheet_name: str = "Rule of 40 Results"


# 例外クラス
class Rule40ScreenerError(Exception):
    """基底例外クラス"""

    pass


class DataFetchError(Rule40ScreenerError):
    """データ取得エラー"""

    pass


class CalculationError(Rule40ScreenerError):
    """計算エラー"""

    pass


class CacheError(Rule40ScreenerError):
    """キャッシュエラー"""

    pass


class ConfigError(Rule40ScreenerError):
    """設定エラー"""

    pass


class ValidationError(Rule40ScreenerError):
    """バリデーションエラー"""

    pass


class ExportError(Rule40ScreenerError):
    """エクスポートエラー"""

    pass
