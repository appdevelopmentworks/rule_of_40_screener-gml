# プロジェクト概要

**名称**: Rule of 40 Screener（デスクトップ版）\
**目的**: 指定した銘柄ユニバースから Rule of 40（%）= 売上高成長率（%） + 営業利益率（%）を算出し、基準を満たす銘柄を抽出・可視化する。SaaS慣行の派生指標（EBITDAマージン版、TTM版、MRQ年率換算版）にも対応。

**主なKPI**

- データ取得成功率 ≥ 98%
- ユニバース5,000銘柄でフル更新所要時間 ≤ 10分（キャッシュ有り時 ≤ 2分）
- スクリーニング結果の再現性（同一日）100%

---

## スコープ（MVP → 拡張）

**MVP**

- 対象市場: 米国（S&P 500 / S&P 400 / Nasdaq & Other listed 全銘柄）
- 銘柄入力: CSV（`symbol,name`）、もしくは指定URL群から取得
- 指標: Rule of 40（営業利益率版・EBITDAマージン版）
- 計算基準: YoY（年次）/ TTM 切替、閾値フィルタ、並び替え、CSVエクスポート
- UI: PySide6 + QFluentWidgets（フレームレス、ダーク/ライト自動切替）
- 配布: PyInstaller（onefolder）

**拡張（将来）**

- 日本株ユニバース（東証上場銘柄）取得アダプタ追加
- 先行指標・早期警戒スコア（例: 売上加速度、粗利率トレンド、RPO/Net Retention 等）
- 履歴保存・日次差分、簡易バックテスト
- Nuitka で高速化、差分更新（ETag/If-Modified-Since）

---

## 想定ユーザー / 主要ユースケース

- **個人/プロ投資家**: 高成長×収益性の両立銘柄の探索
- **クオンツ開発者**: 指標の組み合わせや独自ファクターの検証
- **運用アシスタント**: 日次モニタリング、閾値アラート

---

## データソース（MVP）

**銘柄ユニバース**

- S&P500: Wikipediaページ（HTMLテーブル）
- S&P400: 同上
- Nasdaq/Other: `nasdaqlisted.txt` / `otherlisted.txt`（タブ区切り、ヘッダー付き）

**財務データ**

- `yfinance` 経由の Yahoo Finance
  - 第一候補: `Ticker.info` → `revenueGrowth`（YoY, 小数）/ `operatingMargins`（小数）
  - フォールバック: `income_stmt` / `ttm_income_stmt` / `cashflow` を用いた自前計算

**注**: データは欠損・定義ゆれが起こり得る。算出ロジックに冗長性を持たせる。

---

## 指標定義（運用ポリシー）

**Rule of 40 のバリアント**

1. **OP版（デフォルト）**:\
   R40 = YoY売上成長率（%） + 営業利益率（%）

   - 売上成長率: 年次YoY（もしくはTTM YoY）
   - 営業利益率: `Operating Income / Total Revenue`（同一期間）

2. **EBITDA版（SaaS慣行）**:\
   R40 = YoY売上成長率（%） + EBITDAマージン（%）

   - EBITDA = Operating Income + Depreciation & Amortization
   - マージン = EBITDA / Revenue

3. **MRQ年率換算（オプション）**:\
   直近四半期の売上成長率×4（年率換算）＋ 直近四半期マージン

**単位**: `yfinance`は小数（0.23=23%）→ 表示時に×100。

**欠損時の優先度**

1. `info.revenueGrowth` / `info.operatingMargins` が両方あればそれを採用
2. いずれか欠損→フォールバック計算（TTM優先、次に年次）
3. それでも不可→対象外フラグと理由をUI表示

---

## 設計方針 / アーキテクチャ

**クリーンアーキテクチャ**（関心分離）

- **Adapters**: シンボル取得（Wikipedia, Nasdaq, CSV, JPX…）
- **Data**: Downloader（yfinanceラッパ）, Cache（SQLite）, Parser
- **Domain**: 指標計算（Rule40Calculator, Indicators Plugin）
- **Application**: スクリーニング、フィルタ、ソート、エクスポート
- **UI**: PySide6 + QFluentWidgets（MVVM風）

**スレッディング**

- `QThreadPool + QRunnable` で並列取得（最大同時接続数を制限→Yahoo側に配慮）

**キャッシュ**

- SQLite（`app_data/cache.db`）に財務スナップショットをTTL付き保存（既定=24h）

**ログ**

- `app_data/logs/app_YYYYMMDD.log`（INFO/ERROR, 失敗銘柄一覧）

---

## データモデル（抜粋）

**tables**

- `symbols(symbol TEXT PRIMARY KEY, name TEXT, market TEXT, source TEXT, updated_at DATETIME)`
- `financials(symbol TEXT, period TEXT, kind TEXT, key TEXT, value REAL, asof DATE, PRIMARY KEY(symbol, period, kind, key))`
- `metrics(symbol TEXT PRIMARY KEY, r40_op REAL, r40_ebitda REAL, rev_yoy REAL, opm REAL, ebitda_margin REAL, last_calc DATETIME)`

**period/kind例**

- period: `annual`, `ttm`, `mrq`
- kind: `income_stmt`, `cashflow`, `info`

---

## 計算ロジック（擬似コード）

```python
class Rule40Calculator:
    def compute(self, fin):
        # fin: dict-like { 'rev_annual': pd.Series, 'op_annual': pd.Series, ... }
        rev = fin['rev_annual'].sort_index()
        op  = fin['op_annual'].sort_index()
        # YoY
        rev_yoy = float(rev.iloc[-1] / rev.iloc[-2] - 1) if len(rev) >= 2 else None
        # OPM (latest)
        opm = float(op.iloc[-1] / rev.iloc[-1]) if len(op) and rev.iloc[-1] else None
        # EBITDA margin
        da  = fin.get('da_annual')
        if da is not None and len(da):
            ebitda_margin = float((op.iloc[-1] + da.iloc[-1]) / rev.iloc[-1])
        else:
            ebitda_margin = None
        r40_op = (rev_yoy or 0) * 100 + (opm or 0) * 100 if (rev_yoy is not None and opm is not None) else None
        r40_ebitda = (rev_yoy or 0) * 100 + (ebitda_margin or 0) * 100 if (rev_yoy is not None and ebitda_margin is not None) else None
        return {
            'rev_yoy': rev_yoy, 'opm': opm,
            'ebitda_margin': ebitda_margin,
            'r40_op': r40_op, 'r40_ebitda': r40_ebitda,
        }
```

---

## シンボル取得アダプタ（設計）

```python
class SymbolSource(Protocol):
    def fetch(self) -> list[tuple[str, str]]:  # [(symbol, name), ...]
        ...

class WikipediaSP500(SymbolSource):
    # HTMLテーブル→pandas.read_html→正規化→BRK.B→BRK-B などの置換
    pass

class NasdaqListed(SymbolSource):
    # nasdaqlisted.txt / otherlisted.txt（タブ区切り）をread_csvで読む
    pass

class CSVFile(SymbolSource):
    # 任意のCSV（symbol,name）を読み込み
    pass
```

**シンボル正規化（例）**

- `BRK.B → BRK-B`, `BF.B → BF-B`, `RDS.A → SHEL`（過去銘柄の例は変遷に注意）
- 末尾接尾辞 `.A`, `.B`, `.W`, `.U` などの扱いはオプション化

---

## 財務取得ラッパ

```python
class YFClient:
    def info_margins_growth(self, symbol):
        t = yf.Ticker(symbol)
        inf = t.info or {}
        return inf.get('revenueGrowth'), inf.get('operatingMargins')

    def income_stmt(self, symbol, ttm=False):
        t = yf.Ticker(symbol)
        df = t.ttm_income_stmt if ttm else t.income_stmt
        return df

    def cashflow(self, symbol, ttm=False):
        t = yf.Ticker(symbol)
        df = t.ttm_cashflow if ttm else t.cashflow
        return df
```

---

## スクリーニング仕様

**フィルタ**

- R40基準: `>= 40`（閾値可変）
- どのバリアントを採用するか: `OP` / `EBITDA` / `両方`
- マーケット, セクター, 時価総額帯, 利益率>0 などの追加フィルタ

**並び替え**

- R40降順 / 売上成長率 / マージン / 時価総額 / 直近株価リターン（任意）

**出力**

- 画面テーブル表示（列カスタマイズ可能）
- CSVエクスポート（UTF-8, ヘッダー付き）

---

## UI要件（PySide6 + QFluentWidgets）

- **フレームレス**（ドラッグで移動、角丸、影）
- **自動ダーク/ライト**（OS追従 + 手動トグル）
- **レイアウト**
  - 左サイドバー: データ取得、ユニバース選択、フィルタ、テーマ切替
  - メイン: テーブル（仮想化/高速スクロール）、列ソート、列フィルタ
  - 右ドロワー: 選択銘柄の詳細（財務サマリ、スパークライン、ログ）
- **アニメーション**: ドロワー開閉、行ハイライト、トースト通知

---

## エラーハンドリング / リトライ

- ネットワーク: バックオフ（指数関数＋ジッタ）
- 欠損: 欄外に「欠損理由」バッジ表示（例: info欠損→TTM計算→不可）
- 失敗銘柄: 再取得ボタン、ログへ一覧出力

---

## 性能 / キャッシュ戦略

- 初回: ユニバースを分割して並列取得（同時8～16スレッド）
- 再取得: TTL内はキャッシュ使用、手動で「強制再取得」可
- 差分: 新規/削除銘柄のみ取得（将来）

---

## セキュリティ / 法的配慮

- APIキー不要（`yfinance`）。
- 利用規約に従い大量スクレイピングを避け、適切な間隔を設ける。
- ローカル保存のみ。外部送信なし（オプトインの匿名テレメトリを将来検討）。

---

## 国際化 / アクセシビリティ

- i18n: 日本語/英語翻訳（Qtの`tr()`）
- A11y: キーボード操作、フォントサイズスライダー、カラーブラインド配慮配色

---

## 設定ファイル（例 `config.yaml`）

```yaml
ui:
  theme: auto  # auto | light | dark
  locale: ja
fetch:
  max_workers: 12
  cache_ttl_hours: 24
rule40:
  variant: op   # op | ebitda | both
  period: ttm   # annual | ttm | mrq_annualized
  threshold: 40
universe:
  sources: [sp500, sp400, nasdaq, other]
  csv_path: null
```

---

## ディレクトリ構成（提案）

```
rule40_screener/
  app.py
  core/
    adapters/
      wikipedia_sp500.py
      nasdaq_txt.py
      csv_source.py
    data/
      yf_client.py
      cache.py
    domain/
      rule40.py
      indicators.py  # プラグインIF
      utils.py
  ui/
    main_window.py
    views/
    widgets/
  app_data/
    cache.db
    logs/
  config.yaml
  tests/
    test_rule40.py
    test_adapters.py
  build/
```

---

## プラグインIF（将来の先行指標拡張）

```python
class Indicator(ABC):
    id: str
    name: str
    def compute(self, fin: dict, prices: pd.DataFrame | None) -> pd.Series | float | dict:
        """fin: 財務データ束, prices: 株価（任意）"""
        ...

# 例: 売上加速度（加速度= 今期YoY - 前期YoY）
```

---

## テスト計画

- **ユニット**: YoY計算、マージン計算、シンボル正規化
- **結合**: 10銘柄サンプルで end-to-end（キャッシュ→計算→UI反映）
- **ベンチ**: 5k銘柄で処理時間測定

---

## リリース / 配布

- **PyInstaller**: onefolder、`--add-data`で`config.yaml`同梱、`--noconsole`
- バージョニング: `MAJOR.MINOR.PATCH`
- 変更履歴: `CHANGELOG.md`

---

## 受入基準（MVP）

1. 指定ユニバースの読込が成功し、欠損理由付きで集計できる
2. OP/EBITDA両方式のR40を計算し、閾値で抽出・並び替え可能
3. フレームレスUI、テーマ自動切替が動作
4. CSVエクスポートが正しい列・エンコーディングで出力

---

## 今後の検討（日本株ユニバース）

- 東証上場銘柄一覧（公式CSV/Excelの定期更新）、証券コード→yfinanceティッカー変換（例: `7203.T`）
- セクター/33業種分類の付与、JPデータの休日・決算期の考慮

---

## 次アクション（提案）

1. 本要求定義の差分コメントを反映 → v1.1確定
2. スタブ実装（Adapters/YFClient/Rule40Calculator/UIベース）
3. 最小ユニバース（例: S&P500）でe2e通し → 性能測定
4. 日本株アダプタの仕様固め

