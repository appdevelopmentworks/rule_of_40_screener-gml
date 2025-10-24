# API 設計

## コア API

### 1. SymbolSource API

銘柄データ取得の抽象インターフェース

```python
from typing import List, Tuple, Protocol
from dataclasses import dataclass

@dataclass
class Symbol:
    symbol: str
    name: str
    market: str
    sector: str = ""
    industry: str = ""

class SymbolSource(Protocol):
    """銘柄データ取得の抽象基底クラス"""
    
    def fetch(self) -> List[Symbol]:
        """銘柄リストを取得"""
        ...
    
    def get_source_name(self) -> str:
        """データソース名を取得"""
        ...
    
    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        ...
```

#### 実装例

```python
class WikipediaSP500(SymbolSource):
    def __init__(self, url: str = None):
        self.url = url or "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    def fetch(self) -> List[Symbol]:
        # Wikipedia HTML テーブルをパース
        import pandas as pd
        tables = pd.read_html(self.url)
        df = tables[0]  # 最初のテーブル
        
        symbols = []
        for _, row in df.iterrows():
            symbol = self._normalize_symbol(row['Symbol'])
            name = row['Security']
            sector = row.get('GICS Sector', '')
            industry = row.get('GICS Sub-Industry', '')
            
            symbols.append(Symbol(
                symbol=symbol,
                name=name,
                market="NYSE/NASDAQ",
                sector=sector,
                industry=industry
            ))
        
        return symbols
    
    def _normalize_symbol(self, symbol: str) -> str:
        """シンボルの正規化"""
        # BRK.B → BRK-B, BF.B → BF-B など
        return symbol.replace('.', '-')
```

### 2. YFClient API

yfinance ラッパー

```python
from typing import Optional, Dict, Any
import pandas as pd

@dataclass
class FinancialData:
    symbol: str
    revenue_annual: Optional[pd.Series] = None
    revenue_ttm: Optional[pd.Series] = None
    operating_income_annual: Optional[pd.Series] = None
    operating_income_ttm: Optional[pd.Series] = None
    depreciation_annual: Optional[pd.Series] = None
    info: Optional[Dict[str, Any]] = None
    last_updated: Optional[str] = None

class YFClient:
    """Yahoo Finance データ取得クライアント"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def get_financial_data(self, symbol: str) -> FinancialData:
        """財務データを取得"""
        ...
    
    def get_info_margins_growth(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """info から成長率とマージンを取得"""
        ...
    
    def get_income_statement(self, symbol: str, ttm: bool = False) -> Optional[pd.DataFrame]:
        """損益計算書を取得"""
        ...
    
    def get_cash_flow(self, symbol: str, ttm: bool = False) -> Optional[pd.DataFrame]:
        """キャッシュフロー計算書を取得"""
        ...
```

#### 実装例

```python
import yfinance as yf
from datetime import datetime

class YFClient:
    def get_financial_data(self, symbol: str) -> FinancialData:
        try:
            ticker = yf.Ticker(symbol)
            
            # Info データ取得
            info = ticker.info or {}
            
            # 財務諸表取得
            income_stmt = ticker.income_stmt
            ttm_income_stmt = ticker.ttm_income_stmt
            cashflow = ticker.cashflow
            
            return FinancialData(
                symbol=symbol,
                revenue_annual=income_stmt.loc['Total Revenue'] if income_stmt is not None else None,
                revenue_ttm=ttm_income_stmt.loc['Total Revenue'] if ttm_income_stmt is not None else None,
                operating_income_annual=income_stmt.loc['Operating Income'] if income_stmt is not None else None,
                operating_income_ttm=ttm_income_stmt.loc['Operating Income'] if ttm_income_stmt is not None else None,
                depreciation_annual=cashflow.loc['Depreciation & Amortization'] if cashflow is not None else None,
                info=info,
                last_updated=datetime.now().isoformat()
            )
        except Exception as e:
            raise DataFetchError(f"Failed to fetch data for {symbol}: {e}")
```

### 3. Rule40Calculator API

Rule of 40 計算エンジン

```python
from enum import Enum
from typing import Protocol

class CalculationPeriod(Enum):
    ANNUAL = "annual"
    TTM = "ttm"
    MRQ_ANNUALIZED = "mrq_annualized"

class Rule40Strategy(Protocol):
    """Rule of 40 計算戦略"""
    
    def calculate(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        ...

@dataclass
class Rule40Result:
    symbol: str
    r40_op: Optional[float] = None  # 営業利益版
    r40_ebitda: Optional[float] = None  # EBITDA版
    revenue_growth_yoy: Optional[float] = None
    operating_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    period: CalculationPeriod = CalculationPeriod.TTM
    calculation_time: str = ""
    data_quality: str = "complete"  # complete, partial, missing

class Rule40Calculator:
    """Rule of 40 計算クラス"""
    
    def __init__(self):
        self.op_strategy = OPStrategy()
        self.ebitda_strategy = EBITDAStrategy()
    
    def calculate(self, data: FinancialData, period: CalculationPeriod = CalculationPeriod.TTM) -> Rule40Result:
        """Rule of 40 を計算"""
        ...
    
    def calculate_op(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        """営業利益版を計算"""
        return self.op_strategy.calculate(data, period)
    
    def calculate_ebitda(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        """EBITDA版を計算"""
        return self.ebitda_strategy.calculate(data, period)
```

#### 戦略実装例

```python
class OPStrategy(Rule40Strategy):
    def calculate(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        # 売上成長率計算
        rev_growth = self._calculate_revenue_growth(data, period)
        if rev_growth is None:
            return None
        
        # 営業利益率計算
        op_margin = self._calculate_operating_margin(data, period)
        if op_margin is None:
            return None
        
        return rev_growth * 100 + op_margin * 100
    
    def _calculate_revenue_growth(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        if period == CalculationPeriod.TTM and data.revenue_ttm is not None:
            # TTM データ使用
            if len(data.revenue_ttm) >= 2:
                current = data.revenue_ttm.iloc[0]
                previous = data.revenue_ttm.iloc[1]
                return (current / previous) - 1 if previous != 0 else None
        
        elif period == CalculationPeriod.ANNUAL and data.revenue_annual is not None:
            # 年次データ使用
            if len(data.revenue_annual) >= 2:
                current = data.revenue_annual.iloc[0]
                previous = data.revenue_annual.iloc[1]
                return (current / previous) - 1 if previous != 0 else None
        
        return None
    
    def _calculate_operating_margin(self, data: FinancialData, period: CalculationPeriod) -> Optional[float]:
        if period == CalculationPeriod.TTM:
            if (data.operating_income_ttm is not None and data.revenue_ttm is not None
                and len(data.operating_income_ttm) > 0 and len(data.revenue_ttm) > 0):
                op_income = data.operating_income_ttm.iloc[0]
                revenue = data.revenue_ttm.iloc[0]
                return op_income / revenue if revenue != 0 else None
        
        elif period == CalculationPeriod.ANNUAL:
            if (data.operating_income_annual is not None and data.revenue_annual is not None
                and len(data.operating_income_annual) > 0 and len(data.revenue_annual) > 0):
                op_income = data.operating_income_annual.iloc[0]
                revenue = data.revenue_annual.iloc[0]
                return op_income / revenue if revenue != 0 else None
        
        return None
```

### 4. CacheManager API

キャッシュ管理

```python
from typing import List, Optional
import sqlite3
from datetime import datetime, timedelta

@dataclass
class CacheEntry:
    key: str
    value: str  # JSON serialized data
    created_at: datetime
    expires_at: datetime

class CacheManager:
    """SQLite ベースのキャッシュマネージャ"""
    
    def __init__(self, db_path: str, ttl_hours: int = 24):
        self.db_path = db_path
        self.ttl = timedelta(hours=ttl_hours)
        self._init_db()
    
    def get(self, key: str) -> Optional[Any]:
        """キャッシュからデータを取得"""
        ...
    
    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None):
        """キャッシュにデータを保存"""
        ...
    
    def delete(self, key: str) -> bool:
        """キャッシュを削除"""
        ...
    
    def cleanup(self) -> int:
        """期限切れキャッシュをクリーンアップ"""
        ...
    
    def clear_all(self):
        """全キャッシュをクリア"""
        ...
```

### 5. ScreeningService API

スクリーニング処理

```python
from typing import List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class FilterOperator(Enum):
    GT = "gt"      # Greater than
    GTE = "gte"    # Greater than or equal
    LT = "lt"      # Less than
    LTE = "lte"    # Less than or equal
    EQ = "eq"      # Equal
    NEQ = "neq"    # Not equal

@dataclass
class Filter:
    field: str     # r40_op, r40_ebitda, revenue_growth, etc.
    operator: FilterOperator
    value: float

@dataclass
class SortConfig:
    field: str
    ascending: bool = False

class ProgressCallback(Protocol):
    def __call__(self, current: int, total: int, message: str):
        ...

class ScreeningService:
    """スクリーニング処理サービス"""
    
    def __init__(self, 
                 symbol_sources: List[SymbolSource],
                 yf_client: YFClient,
                 calculator: Rule40Calculator,
                 cache: CacheManager):
        self.symbol_sources = symbol_sources
        self.yf_client = yf_client
        self.calculator = calculator
        self.cache = cache
    
    def screen(self,
               filters: List[Filter],
               sort_config: Optional[SortConfig] = None,
               progress_callback: Optional[ProgressCallback] = None) -> List[Rule40Result]:
        """スクリーニング実行"""
        ...
    
    def get_symbols(self, sources: List[str]) -> List[Symbol]:
        """指定ソースから銘柄リストを取得"""
        ...
    
    def calculate_batch(self, symbols: List[str], 
                       progress_callback: Optional[ProgressCallback] = None) -> List[Rule40Result]:
        """バッチ計算実行"""
        ...
```

## UI API

### 1. MainWindow API

```python
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject

class ScreeningSignals(QObject):
    progress_updated = Signal(int, int, str)  # current, total, message
    screening_completed = Signal(list)  # List[Rule40Result]
    error_occurred = Signal(str)  # error message

class MainWindow(QFrame):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.signals = ScreeningSignals()
        self._setup_ui()
        self._connect_signals()
    
    def start_screening(self, config: ScreeningConfig):
        """スクリーニング開始"""
        ...
    
    def export_results(self, file_path: str, format: str = "csv"):
        """結果をエクスポート"""
        ...
    
    def apply_filters(self, filters: List[Filter]):
        """フィルタを適用"""
        ...
```

### 2. TableView API

```python
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import QAbstractTableModel, Qt

class ScreeningModel(QAbstractTableModel):
    """スクリーニング結果テーブルモデル"""
    
    def __init__(self):
        super().__init__()
        self._results: List[Rule40Result] = []
        self._headers = ["Symbol", "Name", "R40 OP", "R40 EBITDA", "Revenue Growth", "OP Margin"]
    
    def set_results(self, results: List[Rule40Result]):
        """結果を設定"""
        ...
    
    def filter_results(self, filters: List[Filter]):
        """フィルタ適用"""
        ...
    
    def sort_results(self, column: int, order: Qt.SortOrder):
        """ソート実行"""
        ...

class ScreeningTableView(QTableView):
    """スクリーニング結果テーブルビュー"""
    
    def __init__(self):
        super().__init__()
        self.setModel(ScreeningModel())
        self._setup_view()
    
    def export_to_csv(self, file_path: str):
        """CSV エクスポート"""
        ...
```

## 設定 API

### 1. ConfigManager API

```python
from typing import Any, Dict, Optional
from pathlib import Path

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得（ドット区切り対応: ui.theme）"""
        ...
    
    def set(self, key: str, value: Any):
        """設定値を設定"""
        ...
    
    def save(self):
        """設定をファイルに保存"""
        ...
    
    def reload(self):
        """設定を再読み込み"""
        ...
```

## エラーハンドリング API

### 1. 例外階層

```python
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

class UIError(Rule40ScreenerError):
    """UIエラー"""
    pass
```

### 2. リトライ API

```python
import time
import random
from typing import Callable, TypeVar, Type

T = TypeVar('T')

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """リトライデコレータ"""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        break
                    
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
```

この API 設計により、各コンポーネントの責務が明確になり、テスト容易性と拡張性が確保されます。