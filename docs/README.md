# Rule of 40 Screener

デスクトップ版 Rule of 40 スクリーニングアプリケーション

## 概要

指定した銘柄ユニバースから Rule of 40（%）= 売上高成長率（%） + 営業利益率（%）を算出し、基準を満たす銘柄を抽出・可視化するツールです。SaaS慣行の派生指標（EBITDAマージン版、TTM版、MRQ年率換算版）にも対応しています。

## 主な機能

- 🔍 **マルチユニバース対応**: S&P 500, S&P 400, Nasdaq 全銘柄
- 📊 **複数指標**: OP版・EBITDA版の Rule of 40 計算
- 🎯 **柔軟なフィルタリング**: 閾値、セクター、時価総額など
- 📈 **リアルタイム表示**: 高速テーブル表示とソート機能
- 🌓 **モダンUI**: フレームレスデザイン、ダーク/ライトテーマ
- 💾 **データエクスポート**: CSV形式での結果出力
- ⚡ **高速処理**: 並列取得とキャッシュ機能

## 技術スタック

- **言語**: Python 3.9+
- **UI**: PySide6 + QFluentWidgets
- **データソース**: yfinance (Yahoo Finance)
- **キャッシュ**: SQLite
- **配布**: PyInstaller

## クイックスタート

### インストール

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# アプリケーション起動
python app.py
```

### 基本的な使い方

1. **ユニバース選択**: 左サイドバーから分析対象を選択
2. **フィルタ設定**: Rule of 40 閾値や追加条件を設定
3. **データ取得**: 「取得」ボタンで財務データをダウンロード
4. **結果確認**: テーブルでスクリーニング結果を確認
5. **エクスポート**: CSVで結果を保存

## プロジェクト構成

```
rule40_screener/
├── app.py                    # メインエントリーポイント
├── config.yaml              # 設定ファイル
├── core/                    # コアビジネスロジック
│   ├── adapters/           # データ取得アダプタ
│   ├── data/              # データ層（ダウンロード、キャッシュ）
│   └── domain/            # ドメインロジック（指標計算）
├── ui/                     # UI層
│   ├── main_window.py     # メインウィンドウ
│   ├── views/             # 各種ビュー
│   └── widgets/           # カスタムウィジェット
├── app_data/              # アプリケーションデータ
│   ├── cache.db          # SQLiteキャッシュ
│   └── logs/             # ログファイル
└── tests/                # テストコード
```

## Rule of 40 とは

Rule of 40 は SaaS 企業の健全性を評価する指標です。

```
Rule of 40 (%) = 売上高成長率 (%) + 営業利益率 (%)
```

- **40%以上**: 健全な成長と収益性のバランス
- **40%未満**: 成長か収益性のどちらかを改善する必要

### バリエーション

1. **OP版（標準）**: 営業利益率を使用
2. **EBITDA版**: EBITDAマージンを使用（SaaS慣行）
3. **MRQ年率換算**: 直近四半期データの年率換算

## 設定

`config.yaml` で動作をカスタマイズできます：

```yaml
ui:
  theme: auto          # auto | light | dark
  locale: ja          # ja | en

fetch:
  max_workers: 12     # 並列取得数
  cache_ttl_hours: 24 # キャッシュ有効期間

rule40:
  variant: op         # op | ebitda | both
  period: ttm         # annual | ttm | mrq_annualized
  threshold: 40       # スクリーニング閾値

universe:
  sources: [sp500, sp400, nasdaq, other]
  csv_path: null      # カスタムCSVファイルパス
```

## 開発

### 環境構築

```bash
# 開発用依存パッケージ
pip install -r requirements-dev.txt

# テスト実行
pytest tests/

# コードフォーマット
black .
ruff check .
```

### ビルド

```bash
# PyInstaller で実行ファイル作成
pyinstaller --onefile --windowed --add-data "config.yaml:." app.py
```

## ライセンス

MIT License

## 貢献

バグ報告や機能要望は Issues にてお願いします。

---

**注意**: 本アプリケーションは投資助言を目的としていません。投資判断はご自身の責任で行ってください。