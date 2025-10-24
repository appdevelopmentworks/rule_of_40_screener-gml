# Rule of 40 Screener

デスクトップ版 Rule of 40 スクリーニングアプリケーション

## 🚀 プロジェクト概要

指定した銘柄ユニバースから Rule of 40（%）= 売上高成長率（%） + 営業利益率（%）を算出し、基準を満たす銘柄を抽出・可視化するツールです。SaaS慣行の派生指標（EBITDAマージン版、TTM版、MRQ年率換算版）にも対応しています。

## ✨ 主な機能

- 🔍 **マルチユニバース対応**: S&P 500, S&P 400, Nasdaq 全銘柄
- 🌏 **日本株対応**: 4桁の証券コード（例：7203）を自動的に.T形式に変換
- 📊 **複数指標**: OP版・EBITDA版の Rule of 40 計算
- 🎯 **柔軟なフィルタリング**: 閾値、セクター、時価総額など
- 📈 **リアルタイム表示**: 高速テーブル表示とソート機能
- 💾 **データエクスポート**: CSV形式での結果出力（画面右下のボタンから実行）
- ⚡ **高速処理**: 並列取得とキャッシュ機能（SQLiteベース）
- 🗂️ **CSVインポート**: カスタム銘柄リストの読み込み

## 🛠 技術スタック

- **言語**: Python 3.9+
- **UI**: PySide6 (Qt6)
- **データソース**: yfinance (Yahoo Finance)
- **キャッシュ**: SQLite (WALモード)
- **データ処理**: pandas, numpy

## 📁 プロジェクト構成

```
rule_of_40_screener-gml/
├── docs/                           # ドキュメント
│   ├── README.md                   # プロジェクト概要
│   ├── requirements.txt            # 依存パッケージ
│   ├── config.yaml                 # 設定ファイルテンプレート
│   ├── architecture.md             # アーキテクチャ設計
│   ├── api_design.md               # API設計
│   ├── ui_specifications.md        # UI仕様
│   └── development_guide.md        # 開発ガイド
├── src/                            # ソースコード
│   ├── app.py                      # メインエントリーポイント
│   ├── config.yaml                 # 実行時設定ファイル
│   ├── core/                       # コアビジネスロジック
│   │   ├── adapters/               # データ取得アダプタ
│   │   │   ├── base.py             # 基底クラス
│   │   │   ├── wikipedia_sp500.py  # Wikipedia S&P500/400
│   │   │   ├── nasdaq_txt.py       # Nasdaq銘柄リスト
│   │   │   └── csv_source.py       # CSVファイル読込
│   │   ├── data/                   # データ層
│   │   │   ├── cache.py            # SQLiteキャッシュ
│   │   │   ├── config_loader.py    # 設定管理
│   │   │   └── yf_client.py        # Yahoo Finance API
│   │   ├── domain/                 # ドメインロジック
│   │   │   ├── models.py           # データモデル
│   │   │   └── rule40.py           # Rule of 40計算
│   │   └── application/            # アプリケーション層
│   │       ├── screening_service.py # スクリーニングサービス
│   │       └── export_service.py   # エクスポート機能
│   ├── ui/                         # UI層
│   │   ├── main_window.py          # メインウィンドウ
│   │   ├── widgets/                # UIコンポーネント
│   │   │   ├── side_bar.py         # サイドバー
│   │   │   └── results_table.py    # 結果テーブル
│   │   └── workers/                # バックグラウンド処理
│   │       └── screening_worker.py # スクリーニングワーカー
│   └── app_data/                   # アプリケーションデータ
│       ├── cache/                  # キャッシュDB
│       └── logs/                   # ログファイル
├── interact/                       # サンプルCSVファイル置き場
├── tests/                          # テストコード
└── venv/                           # Python仮想環境
```

## 🚀 導入方法

### 必要要件

- **Python 3.9 以上**
- **pip** (Pythonパッケージマネージャ)
- **インターネット接続** (Yahoo Finance APIへのアクセスに必要)

### ステップ1: リポジトリの取得

```bash
# リポジトリをクローン（またはZIPダウンロード）
git clone <repository-url>
cd rule_of_40_screener-gml
```

### ステップ2: 仮想環境の作成

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows (コマンドプロンプト)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### ステップ3: 依存パッケージのインストール

```bash
# 必要なパッケージをインストール
pip install -r docs/requirements.txt
```

**主な依存パッケージ:**
- PySide6 (Qt6 GUI)
- yfinance (Yahoo Finance API)
- pandas (データ処理)
- requests (HTTP通信)
- openpyxl (Excelエクスポート)

### ステップ4: アプリケーション起動

```bash
# アプリケーションを起動
python src/app.py
```

初回起動時には以下のディレクトリとファイルが自動生成されます：
- `src/app_data/cache/` - キャッシュデータベース
- `src/app_data/logs/` - アプリケーションログ

## 📖 基本的な使い方

### 1. データソースの選択

左サイドバーから分析対象を選択：
- **S&P 500**: 米国大型株
- **S&P 400**: 米国中型株
- **Nasdaq**: Nasdaq上場全銘柄
- **Other**: その他市場
- **CSV**: カスタム銘柄リスト

### 2. フィルタ設定

- **Rule of 40 バリアント**: OP版 / EBITDA版 / 両方
- **期間**: TTM / 年次 / MRQ年率換算
- **閾値**: Rule of 40の最小値（デフォルト: 40.0）
- **最小売上高**: 時価総額フィルター
- **黒字のみ**: 利益率プラスの銘柄のみ

### 3. スクリーニング実行

「スクリーニング開始」ボタンをクリック
- 進捗状況がステータスバーに表示されます
- 完了すると結果テーブルに表示されます

### 4. 結果の確認と絞り込み

- **ソート**: 列ヘッダーをクリック
- **検索**: 上部の検索ボックスでフィルタリング
- **バリアント切替**: ドロップダウンでOP版/EBITDA版を切替

### 5. CSV出力

画面右下の「CSV出力」ボタンをクリック
- 保存先を選択してエクスポート
- UTF-8（BOM付き）形式で保存（Excel対応）

### CSVファイルのインポート

#### 米国株の場合
```csv
symbol
AAPL
MSFT
GOOGL
```

#### 日本株の場合
```csv
symbol
7203
9984
6758
```

**注意**: 4桁の数字は自動的に`.T`接尾辞が追加されます（例：`7203` → `7203.T`）

左サイドバーの「CSVを開く」ボタンからファイルを読み込めます。

## 📊 Rule of 40 とは

Rule of 40 は SaaS 企業の健全性を評価する指標です。

```
Rule of 40 (%) = 売上高成長率 (%) + 営業利益率 (%)
```

- **40%以上**: 健全な成長と収益性のバランス
- **40%未満**: 成長か収益性のどちらかを改善する必要

### バリエーション

1. **OP版（標準）**: 営業利益率を使用
   - `Rule of 40 (OP) = 売上成長率 + 営業利益率`

2. **EBITDA版**: EBITDAマージンを使用（SaaS慣行）
   - `Rule of 40 (EBITDA) = 売上成長率 + EBITDAマージン`

3. **期間の選択**:
   - **TTM** (Trailing Twelve Months): 直近12ヶ月
   - **Annual**: 年次決算
   - **MRQ年率換算**: 直近四半期の年率換算

## ⚙️ 設定

`src/config.yaml` で動作をカスタマイズできます：

```yaml
ui:
  theme: auto          # auto | light | dark
  locale: ja           # ja | en
  window:
    width: 1200
    height: 800

fetch:
  max_workers: 12      # 並列取得数（推奨: 2-12）
  cache_ttl_hours: 24  # キャッシュ有効期間（時間）

cache:
  path: src/app_data/cache/screening.db
  ttl_hours: 24

rule40:
  variant: op          # op | ebitda | both
  period: ttm          # annual | ttm | mrq_annualized
  threshold: 40.0      # スクリーニング閾値

universe:
  sources: [sp500, sp400, nasdaq, other]
  csv_path: null       # カスタムCSVファイルパス
```

## 🗄️ データベース（キャッシュ）について

本アプリケーションはSQLiteを**キャッシュ専用**で使用します。

### 保存される内容
- Yahoo Financeから取得した財務データ
- 有効期限: デフォルト24時間

### 保存されない内容
- ❌ スクリーニング結果
- ❌ ユーザー設定
- ❌ 銘柄リスト
- ❌ 過去のスクリーニング履歴

### キャッシュのクリア方法
1. UIの「キャッシュクリア」ボタン
2. ファイル削除: `src/app_data/cache/screening.db`

## 🐛 トラブルシューティング

### スクリーニング結果が0件

1. **閾値を下げる**: Rule of 40が40を超える企業は少ないため、閾値を10-20に設定
2. **フィルターを確認**: 最小売上高や黒字フィルターを無効化
3. **キャッシュをクリア**: 古いデータが残っている可能性

### データ取得エラー

1. **インターネット接続を確認**
2. **Yahoo Financeのレート制限**: 少し待ってから再実行
3. **並列数を減らす**: `config.yaml`の`max_workers`を2-4に設定

### 日本株が取得できない

- CSVに4桁の数字のみが記載されているか確認
- 自動的に`.T`接尾辞が追加されているかログで確認

### データベースロックエラー

- アプリケーションを再起動
- キャッシュデータベースを削除して再起動

## 🧪 開発者向け情報

### 開発環境セットアップ

```bash
# 開発用依存パッケージ
pip install -r docs/requirements.txt

# コードフォーマット（オプション）
pip install black ruff

# フォーマット実行
black src/
ruff check src/
```

### ログの確認

```bash
# ログファイルの場所
tail -f src/app_data/logs/app_YYYYMMDD.log
```

### テストCSVの作成

```bash
# interact/ディレクトリにサンプルCSVを配置
echo "symbol" > interact/test_stocks.csv
echo "AAPL" >> interact/test_stocks.csv
echo "MSFT" >> interact/test_stocks.csv
```

## 📋 開発状況

### ✅ 完了機能

- [x] S&P 500/400、Nasdaqからのデータ取得
- [x] 日本株対応（自動.T接尾辞追加）
- [x] Rule of 40計算（OP版・EBITDA版）
- [x] リアルタイムスクリーニング
- [x] CSVインポート・エクスポート
- [x] キャッシュ機能（SQLite WALモード）
- [x] User-Agent設定によるアクセス制限回避
- [x] データベースロック問題の修正
- [x] 閾値フィルタリング
- [x] UIからのCSV出力ボタン

### 🚧 今後の予定

- [ ] Excel形式のエクスポート
- [ ] 日本株専用ユニバース対応
- [ ] 先行指標・早期警戒スコア
- [ ] 履歴保存・日次差分
- [ ] パフォーマンス最適化
- [ ] 実行ファイル配布（PyInstaller/Nuitka）

## 🤝 貢献

バグ報告や機能要望は Issues にてお願いします。

## 📄 ライセンス

MIT License

## ⚠️ 免責事項

本アプリケーションは投資助言を目的としていません。提供されるデータは参考情報であり、投資判断はご自身の責任で行ってください。Yahoo Finance APIの利用規約を遵守してご使用ください。

---

**開発状況**: アクティブ開発中 🚧
**最終更新**: 2025-10-24
