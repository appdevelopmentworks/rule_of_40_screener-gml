# 開発ガイド

## 開発環境セットアップ

### 1. 前提条件

- Python 3.9 以上
- Git
- Visual Studio Code (推奨) または PyCharm

### 2. 環境構築

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd rule_of_40_screener-gml

# 2. 仮想環境作成
python -m venv venv

# 3. 仮想環境有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 依存パッケージインストール
pip install -r docs/requirements.txt

# 5. 開発用ツールインストール
pip install pytest pytest-asyncio black ruff mypy pre-commit

# 6. pre-commit 設定
pre-commit install
```

### 3. VS Code 設定

`.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

## プロジェクト構造

```
rule_of_40_screener-gml/
├── docs/                           # ドキュメント
│   ├── README.md                   # プロジェクト概要
│   ├── requirements.txt            # 依存パッケージ
│   ├── config.yaml                 # 設定ファイルテンプレート
│   ├── architecture.md             # アーキテクチャ設計
│   ├── api_design.md              # API設計
│   ├── ui_specifications.md       # UI仕様
│   └── development_guide.md       # 開発ガイド（このファイル）
├── src/                           # ソースコード
│   ├── app.py                     # メインエントリーポイント
│   ├── config.yaml               # 実行時設定ファイル
│   ├── core/                     # コアビジネスロジック
│   │   ├── __init__.py
│   │   ├── adapters/             # データ取得アダプタ
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # 基底クラス
│   │   │   ├── wikipedia_sp500.py
│   │   │   ├── nasdaq_txt.py
│   │   │   └── csv_source.py
│   │   ├── data/                 # データ層
│   │   │   ├── __init__.py
│   │   │   ├── yf_client.py      # yfinance ラッパー
│   │   │   ├── cache.py          # キャッシュ管理
│   │   │   └── config_loader.py  # 設定読み込み
│   │   ├── domain/               # ドメインロジック
│   │   │   ├── __init__.py
│   │   │   ├── rule40.py         # Rule of 40 計算
│   │   │   ├── indicators.py     # 指標プラグイン
│   │   │   ├── models.py         # データモデル
│   │   │   └── utils.py          # ユーティリティ
│   │   └── application/          # アプリケーション層
│   │       ├── __init__.py
│   │       ├── screening_service.py
│   │       ├── filter_service.py
│   │       └── export_service.py
│   ├── ui/                       # UI層
│   │   ├── __init__.py
│   │   ├── main_window.py        # メインウィンドウ
│   │   ├── views/                # 各種ビュー
│   │   │   ├── __init__.py
│   │   │   ├── screening_view.py
│   │   │   ├── filter_panel.py
│   │   │   └── detail_panel.py
│   │   ├── widgets/              # カスタムウィジェット
│   │   │   ├── __init__.py
│   │   │   ├── title_bar.py
│   │   │   ├── side_bar.py
│   │   │   ├── data_table.py
│   │   │   └── progress_widget.py
│   │   └── themes/               # テーマ関連
│   │       ├── __init__.py
│   │       ├── theme_manager.py
│   │       └── style.qss
│   ├── app_data/                 # アプリケーションデータ
│   │   ├── cache.db             # SQLiteキャッシュ
│   │   └── logs/                # ログファイル
│   └── resources/               # リソースファイル
│       ├── icons/               # アイコン
│       └── styles/              # スタイルシート
├── tests/                       # テストコード
│   ├── __init__.py
│   ├── conftest.py              # pytest設定
│   ├── unit/                    # ユニットテスト
│   │   ├── test_rule40.py
│   │   ├── test_adapters.py
│   │   └── test_cache.py
│   ├── integration/             # 結合テスト
│   │   ├── test_screening.py
│   │   └── test_ui.py
│   └── fixtures/                # テストデータ
│       ├── sample_symbols.csv
│       └── mock_financial_data.json
├── build/                       # ビルド関連
│   ├── build.py                 # ビルドスクリプト
│   └── pyinstaller.spec        # PyInstaller設定
├── scripts/                     # 各種スクリプト
│   ├── setup_dev.py            # 開発環境セットアップ
│   └── run_tests.py            # テスト実行
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml              # プロジェクト設定
└── README.md                   # プロジェクトルートREADME
```

## 開発ワークフロー

### 1. ブランチ戦略

```
main                    # 本番ブランチ
├── develop            # 開発ブランチ
├── feature/xxx        # 機能開発ブランチ
├── bugfix/xxx         # バグ修正ブランチ
└── hotfix/xxx         # 緊急修正ブランチ
```

### 2. コミットメッセージ規約

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードフォーマット
- `refactor`: リファクタリング
- `test`: テスト関連
- `chore`: ビルド、設定など

**例**:
```
feat(ui): add dark theme support

Implement theme switching functionality with
automatic OS theme detection and manual toggle.

Closes #123
```

### 3. 開発手順

```bash
# 1. develop ブランチを最新化
git checkout develop
git pull origin develop

# 2. 機能ブランチ作成
git checkout -b feature/add-japanese-stock-support

# 3. 開発とコミット
git add .
git commit -m "feat(data): add Japanese stock adapter"

# 4. テスト実行
pytest tests/

# 5. コードフォーマットとリント
black .
ruff check .

# 6. プッシュとPR作成
git push origin feature/add-japanese-stock-support
# GitHubでPRを作成
```

## コーディング規約

### 1. Python コーディングスタイル

- PEP 8 準拠（Black で自動フォーマット）
- 行長: 88文字（Black デフォルト）
- インデント: 4スペース
- 文字列: ダブルクォート優先

### 2. 命名規約

```python
# クラス: PascalCase
class Rule40Calculator:
    pass

# 関数・変数: snake_case
def calculate_revenue_growth():
    revenue_growth = 0.15
    return revenue_growth

# 定数: UPPER_SNAKE_CASE
DEFAULT_CACHE_TTL_HOURS = 24

# プライベート: アンダースコア1つ
class MyClass:
    def _private_method(self):
        pass
    
    def __very_private(self):
        pass

# ファイル名: snake_case
rule40_calculator.py
screening_service.py
```

### 3. 型ヒント

```python
from typing import List, Optional, Dict, Any, Protocol
from dataclasses import dataclass

@dataclass
class FinancialData:
    symbol: str
    revenue_annual: Optional[pd.Series] = None
    operating_margin: Optional[float] = None

class SymbolSource(Protocol):
    def fetch(self) -> List[Symbol]:
        ...

def calculate_rule40(data: FinancialData, period: str = "ttm") -> Optional[float]:
    """Rule of 40 を計算する"""
    ...
```

### 4. ドキュメンテーション

```python
def calculate_rule40(
    data: FinancialData, 
    period: str = "ttm",
    variant: str = "op"
) -> Optional[float]:
    """
    Rule of 40 を計算する
    
    Args:
        data: 財務データ
        period: 計算期間 ("annual", "ttm", "mrq_annualized")
        variant: 計算バリアント ("op", "ebitda")
    
    Returns:
        Rule of 40 値（%）。計算不可能な場合は None
    
    Raises:
        CalculationError: 計算に必要なデータが不足している場合
    
    Example:
        >>> data = FinancialData(symbol="AAPL", ...)
        >>> result = calculate_rule40(data, "ttm", "op")
        >>> print(f"R40: {result:.1f}%")
    """
    ...
```

## テスト

### 1. テスト戦略

- **ユニットテスト**: 各関数・クラスの単体テスト
- **結合テスト**: 複数コンポーネントの連携テスト
- **UIテスト**: ユーザーインタラクションのテスト
- **パフォーマンステスト**: 大量データ処理のテスト

### 2. テスト実行

```bash
# 全テスト実行
pytest

# 特定ファイルのテスト
pytest tests/unit/test_rule40.py

# カバレッジ計測
pytest --cov=src --cov-report=html

# 特定マーク付きテスト実行
pytest -m "unit"  # ユニットテストのみ
pytest -m "integration"  # 結合テストのみ
```

### 3. テスト記述例

```python
import pytest
from unittest.mock import Mock, patch
from src.core.domain.rule40 import Rule40Calculator
from src.core.domain.models import FinancialData

class TestRule40Calculator:
    
    @pytest.fixture
    def calculator(self):
        return Rule40Calculator()
    
    @pytest.fixture
    def sample_data(self):
        return FinancialData(
            symbol="AAPL",
            revenue_annual=pd.Series([365817, 394328], index=[2022, 2023]),
            operating_income_annual=pd.Series([119437, 114301], index=[2022, 2023])
        )
    
    def test_calculate_op_variant(self, calculator, sample_data):
        """OP版のRule of 40計算テスト"""
        result = calculator.calculate(sample_data, "annual")
        
        assert result is not None
        assert result.r40_op is not None
        assert result.revenue_growth_yoy == pytest.approx(0.078, rel=1e-3)
        assert result.operating_margin == pytest.approx(0.290, rel=1e-3)
        assert result.r40_op == pytest.approx(36.8, rel=1e-1)
    
    def test_insufficient_data(self, calculator):
        """データ不足時のテスト"""
        insufficient_data = FinancialData(symbol="TEST")
        result = calculator.calculate(insufficient_data)
        
        assert result.r40_op is None
        assert result.data_quality == "missing"
    
    @patch('src.core.data.yf_client.yf.Ticker')
    def test_data_fetch_error_handling(self, mock_ticker, calculator):
        """データ取得エラーのハンドリングテスト"""
        mock_ticker.side_effect = Exception("Network error")
        
        with pytest.raises(DataFetchError):
            calculator.get_financial_data("INVALID")
```

## デバッグ

### 1. ログ設定

```python
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_data/logs/debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def calculate_rule40(data):
    logger.debug(f"Calculating Rule of 40 for {data.symbol}")
    try:
        result = _do_calculation(data)
        logger.info(f"Calculation successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Calculation failed: {e}", exc_info=True)
        raise
```

### 2. デバッグ実行

```bash
# デバッグモードで実行
python -m pdb src/app.py

# VS Code デバッガ設定
# .vscode/launch.json
{
    "name": "Python: Debug App",
    "type": "python",
    "request": "launch",
    "program": "src/app.py",
    "console": "integratedTerminal",
    "env": {
        "DEBUG": "1"
    }
}
```

## パフォーマンス最適化

### 1. プロファイリング

```python
import cProfile
import pstats

def profile_function():
    pr = cProfile.Profile()
    pr.enable()
    
    # プロファイリング対象のコード
    result = screening_service.screen(filters)
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### 2. メモリ使用量監視

```python
import tracemalloc

tracemalloc.start()

# コード実行
result = screening_service.screen(filters)

# メモリ使用量取得
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

## ビルドと配布

### 1. 開発ビルド

```bash
# 開発モードで実行
python src/app.py --debug

# ホットリロード（開発中）
watchdog src/app.py
```

### 2. 本番ビルド

```bash
# PyInstaller でビルド
pyinstaller build/pyinstaller.spec

# またはコマンドラインで
pyinstaller --onefile --windowed --add-data "src/config.yaml:." src/app.py
```

### 3. インストーラ作成

```bash
# Windows (NSIS)
makensis installer.nsi

# macOS (.dmg)
create-dmg --volname "Rule of 40 Screener" dist/app.app

# Linux (.AppImage)
appimagetool AppDir Rule40Screener.AppImage
```

## トラブルシューティング

### 1. よくある問題

**Q: yfinance でデータ取得に失敗する**
A: ネットワーク接続を確認し、リトライ設定を調整

```python
# config.yaml
fetch:
  timeout_seconds: 60
  retry_attempts: 5
  backoff_factor: 2
```

**Q: UI がフリーズする**
A: 長時間処理はワーカースレッドで実行

```python
# メインスレッドで実行しない
def on_fetch_clicked(self):
    worker = ScreeningWorker()
    worker.signals.progress.connect(self.update_progress)
    worker.signals.finished.connect(self.on_finished)
    QThreadPool.globalInstance().start(worker)
```

**Q: メモリ使用量が多い**
A: キャッシュサイズを調整し、不要なデータを解放

```python
# config.yaml
cache:
  max_cache_size_mb: 200
  cleanup_interval_hours: 12
```

### 2. デバッグツール

- **Qt Inspector**: UI デバッグ
- **SQLite Browser**: キャッシュ確認
- **Network Monitor**: 通信確認
- **Memory Profiler**: メモリリーク検出

この開発ガイドに従うことで、効率的で保守性の高い開発が可能になります。