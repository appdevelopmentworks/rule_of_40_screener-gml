# UI 仕様詳細

## 全体デザイン

### デザイン原則

1. **モダン & ミニマル**: 不要な要素を排除し、情報に集中
2. **フレームレス**: ウィンドウ枠なしのモダンな外観
3. **ダーク/ライト対応**: OS テーマに自動追従 + 手動切替
4. **レスポンシブ**: ウィンドウサイズに応じたレイアウト調整
5. **高速操作**: キーボードショートカット充実

### カラーテーマ

#### ライトテーマ
```css
--primary: #0078d4
--primary-hover: #106ebe
--background: #ffffff
--surface: #f3f2f1
--text-primary: #323130
--text-secondary: #605e5c
--border: #edebe9
--success: #107c10
--warning: #ff8c00
--error: #d13438
```

#### ダークテーマ
```css
--primary: #4080ff
--primary-hover: #2b5ce6
--background: #1e1e1e
--surface: #2d2d2d
--text-primary: #ffffff
--text-secondary: #cccccc
--border: #3f3f3f
--success: #13a10e
--warning: #ff9500
--error: #e74856
```

## レイアウト構成

### メインウィンドウ

```
┌─────────────────────────────────────────────────────────────┐
│ タイトルバー (ドラッグ可能)                    [─][□][×]    │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│   サイドバー │              メインエリア                     │
│             │                                               │
│ ┌─────────┐ │ ┌─────────────────────────────────────────┐   │
│ │ユニバース│ │ │           テーブルヘッダー              │   │
│ │選択     │ │ └─────────────────────────────────────────┘   │
│ └─────────┘ │ ┌─────────────────────────────────────────┐   │
│             │ │                                         │   │
│ ┌─────────┐ │ │           データテーブル                 │   │
│ │フィルタ │ │ │                                         │   │
│ │設定     │ │ │                                         │   │
│ └─────────┘ │ │                                         │   │
│             │ └─────────────────────────────────────────┘   │
│ ┌─────────┐ │                                               │
│ │操作     │ │                                               │
│ │ボタン   │ │                                               │
│ └─────────┘ │                                               │
├─────────────┼───────────────────────────────────────────────┤
│ ステータスバー                                                │
└─────────────────────────────────────────────────────────────┘
```

### ウィンドウサイズ

- **最小サイズ**: 1000x600
- **推奨サイズ**: 1400x900
- **初期サイズ**: 1200x800
- **位置記憶**: 前回終了時の位置を記憶

## コンポーネント詳細

### 1. タイトルバー

```python
class TitleBar(QFrame):
    """カスタムタイトルバー"""
    
    # コンポーネント
    - app_icon: QLabel      # アプリアイコン
    - app_title: QLabel     # アプリ名
    - spacer: QWidget       # スペーサー
    - theme_toggle: QPushButton  # テーマ切替ボタン
    - minimize_btn: QPushButton  # 最小化ボタン
    - maximize_btn: QPushButton  # 最大化ボタン
    - close_btn: QPushButton     # 閉じるボタン
    
    # 機能
    - ドラッグでウィンドウ移動
    - ダブルクリックで最大化/復元
    - 右クリックでシステムメニュー
```

**仕様**:
- 高さ: 32px
- 背景: テーマに応じた色
- ボタン: ホバーエフェクト、ツールチップ

### 2. サイドバー

```python
class SideBar(QFrame):
    """左サイドバー"""
    
    # セクション
    - universe_section: UniverseSection
    - filter_section: FilterSection  
    - action_section: ActionSection
    - settings_section: SettingsSection
    
    # 機能
    - 折りたたみ可能（幅: 280px → 60px）
    - スクロール対応
    - セクション間の区切り線
```

#### 2.1 UniverseSection

```python
class UniverseSection(QCollapsibleFrame):
    """ユニバース選択セクション"""
    
    # コンポーネント
    - title: QLabel           # "データソース"
    - sp500_checkbox: QCheckBox
    - sp400_checkbox: QCheckBox  
    - nasdaq_checkbox: QCheckBox
    - other_checkbox: QCheckBox
    - csv_file_button: QPushButton  # "CSVファイル選択"
    - csv_path_label: QLabel       # 選択中のCSVパス
    - symbol_count_label: QLabel   # "選択銘柄数: 0"
    
    # 機能
    - チェックボックスの状態で銘柄数を更新
    - CSVファイル選択ダイアログ
    - バリデーション（少なくとも1つ選択）
```

#### 2.2 FilterSection

```python
class FilterSection(QCollapsibleFrame):
    """フィルタ設定セクション"""
    
    # コンポーネント
    - title: QLabel                    # "フィルタ設定"
    - variant_combo: QComboBox         # "指標種別" (OP/EBITDA/両方)
    - period_combo: QComboBox          # "期間" (年次/TTM/MRQ年率)
    - threshold_spinbox: QDoubleSpinBox # "R40閾値" (0-100)
    - min_revenue_spinbox: QSpinBox    # "最低売上" (M USD)
    - margin_positive_checkbox: QCheckBox  # "利益率プラスのみ"
    - sector_combo: QComboBox          # "セクター" (全て/特定)
    - market_cap_combo: QComboBox      # "時価総額" (全て/範囲指定)
    
    # 機能
    - リアルタイムでフィルタ条件をプレビュー
    - 設定の保存/読み込み
    - リセットボタン
```

#### 2.3 ActionSection

```python
class ActionSection(QFrame):
    """操作ボタンセクション"""
    
    # コンポーネント
    - fetch_button: QPushButton    # "データ取得" (プライマリ)
    - stop_button: QPushButton     # "停止" (非表示→表示)
    - refresh_button: QPushButton  # "再取得" (セカンダリ)
    - clear_cache_button: QPushButton  # "キャッシュクリア"
    - export_button: QPushButton   # "エクスポート"
    
    # 機能
    - 取得中はプログレス表示
    - ボタンの有効/無効状態管理
    - ショートカットキー対応
```

### 3. メインエリア

#### 3.1 テーブルヘッダー

```python
class TableHeaderBar(QFrame):
    """テーブル上部ツールバー"""
    
    # コンポーネント
    - search_box: QLineEdit        # 検索ボックス
    - column_selector: QPushButton  # "列選択" ドロップダウン
    - view_combo: QComboBox        # "表示" (テーブル/カード)
    - stats_label: QLabel          # "X件中Y件が条件一致"
    - refresh_table_btn: QPushButton  # テーブル更新
    
    # 機能
    - リアルタイム検索
    - 列の表示/非表示切り替え
    - 統計情報の表示
```

#### 3.2 データテーブル

```python
class ScreeningTableView(QTableView):
    """スクリーニング結果テーブル"""
    
    # 列定義
    columns = [
        {"id": "symbol", "name": "銘柄", "width": 80, "align": "left"},
        {"id": "name", "name": "名称", "width": 200, "align": "left"},
        {"id": "r40_op", "name": "R40 OP", "width": 80, "align": "right", "format": ".1f"},
        {"id": "r40_ebitda", "name": "R40 EBITDA", "width": 100, "align": "right", "format": ".1f"},
        {"id": "revenue_growth", "name": "売上成長率", "width": 100, "align": "right", "format": ".1f"},
        {"id": "op_margin", "name": "営業利益率", "width": 100, "align": "right", "format": ".1f"},
        {"id": "ebitda_margin", "name": "EBITDAマージン", "width": 120, "align": "right", "format": ".1f"},
        {"id": "market_cap", "name": "時価総額", "width": 100, "align": "right", "format": ".0f"},
        {"id": "sector", "name": "セクター", "width": 150, "align": "left"},
        {"id": "data_quality", "name": "品質", "width": 60, "align": "center"}
    ]
    
    # 機能
    - 仮想化スクロール（大量データ対応）
    - 列ソート（クリックで昇順/降順/なし）
    - 列リサイズ（ドラッグ）
    - 行選択（単一/複数）
    - コンテキストメニュー
    - キーボードナビゲーション
    - セルのツールチップ
    - 条件付き書式（色付け）
```

##### 条件付き書式ルール

```python
conditional_formats = {
    "r40_op": [
        {"condition": ">= 40", "background": "#d4edda", "text": "#155724"},
        {"condition": ">= 30", "background": "#fff3cd", "text": "#856404"},
        {"condition": "< 0", "background": "#f8d7da", "text": "#721c24"}
    ],
    "revenue_growth": [
        {"condition": ">= 0.5", "background": "#d1ecf1", "text": "#0c5460"},
        {"condition": "< 0", "background": "#f8d7da", "text": "#721c24"}
    ],
    "data_quality": [
        {"value": "complete", "background": "#d4edda", "text": "#155724"},
        {"value": "partial", "background": "#fff3cd", "text": "#856404"},
        {"value": "missing", "background": "#f8d7da", "text": "#721c24"}
    ]
}
```

#### 3.3 詳細パネル

```python
class DetailPanel(QFrame):
    """選択銘柄詳細パネル（右ドロワー）"""
    
    # コンポーネント
    - header: QFrame            # 銘柄名と基本情報
    - tabs: QTabWidget          # タブ切り替え
        - financial_tab: FinancialSummaryTab
        - chart_tab: ChartTab
        - history_tab: HistoryTab
        - notes_tab: NotesTab
    
    # 機能
    - スライドイン/アウトアニメーション
    - リサイズ可能
    - 非表示状態を記憶
```

### 4. ステータスバー

```python
class StatusBar(QStatusBar):
    """ステータスバー"""
    
    # コンポーネント
    - status_label: QLabel       # "準備完了"
    - progress_bar: QProgressBar # 進捗バー
    - symbol_count_label: QLabel # "銘柄数: 0"
    - cache_status_label: QLabel # "キャッシュ: 有効"
    - last_update_label: QLabel  # "最終更新: --:--"
    
    # 機能
    - 状態のリアルタイム表示
    - 進捗のアニメーション
    - クリック可能な要素
```

## インタラクション

### 1. ユーザーフロー

#### 基本的な操作フロー

```
1. アプリ起動
   ↓
2. ユニバース選択（デフォルト: S&P 500）
   ↓
3. フィルタ設定（デフォルト: R40 >= 40）
   ↓
4. 「データ取得」クリック
   ↓
5. 進捗表示 + 結果テーブル更新
   ↓
6. 結果の確認・フィルタリング・ソート
   ↓
7. 詳細確認 or CSVエクスポート
```

#### 詳細表示フロー

```
テーブル行クリック
   ↓
右ドロワースライドイン
   ↓
財務サマリー表示
   ↓
タブ切り替えで詳細情報
   ↓
閉じるボタン or ESCキーで非表示
```

### 2. キーボードショートカット

| ショートカット | 機能 |
|--------------|------|
| Ctrl+O       | CSVファイルを開く |
| Ctrl+S       | 結果をCSV保存 |
| Ctrl+R       | データ再取得 |
| Ctrl+F       | 検索ボックスにフォーカス |
| Ctrl+T       | テーマ切替 |
| F5           | テーブル更新 |
| ESC          | 検索クリア / 詳細パネル閉じる |
| Ctrl+1~9     | 列選択のショートカット |
| Ctrl+Plus    | テーブルズームイン |
| Ctrl+Minus   | テーブルズームアウト |
| Ctrl+0       | ズームリセット |

### 3. コンテキストメニュー

#### テーブル行コンテキストメニュー

```
銘柄詳細を表示 (Enter)
------------------------
Yahoo Financeで開く (Ctrl+Y)
シンボルをクリップボードにコピー (Ctrl+C)
------------------------
この銘柄を除外 (Delete)
------------------------
CSVに行をエクスポート
```

#### テーブルヘッダーコンテキストメニュー

```
列の表示/非表示
------------------------
この列でソート
------------------------
列幅を自動調整
全列幅を自動調整
------------------------
この列を固定
```

## アニメーション

### 1. トランジション効果

```python
# ドロワースライド
slide_in = QPropertyAnimation(detail_panel, b"geometry")
slide_in.setDuration(300)
slide_in.setEasingCurve(QEasingCurve.OutCubic)

# フェードイン
fade_in = QPropertyAnimation(widget, b"windowOpacity")
fade_in.setDuration(200)
fade_in.setStartValue(0.0)
fade_in.setEndValue(1.0)

# ボタンホバー
hover_effect = QGraphicsColorizeEffect()
hover_effect.setColor(QColor("#4080ff"))
hover_effect.setStrength(0.3)
```

### 2. ローディングアニメーション

```python
class LoadingSpinner(QLabel):
    """ローディングスピナー"""
    
    def __init__(self):
        super().__init__()
        self.movie = QMovie(":/icons/loading.gif")
        self.setMovie(self.movie)
    
    def start(self):
        self.movie.start()
    
    def stop(self):
        self.movie.stop()
```

## レスポンシブデザイン

### 1. ブレークポイント

```python
breakpoints = {
    "small": 1000,   # サイドバー自動折りたたみ
    "medium": 1200,  # 通常表示
    "large": 1600    # 拡張表示
}
```

### 2. アダプティブレイアウト

```python
def update_layout(width):
    if width < breakpoints["small"]:
        # 小画面: サイドバー折りたたみ、テーブル列削減
        side_bar.collapse()
        table.hide_columns(["sector", "industry"])
    elif width < breakpoints["medium"]:
        # 中画面: 通常表示
        side_bar.expand()
        table.show_all_columns()
    else:
        # 大画面: 拡張表示
        table.show_extra_columns(["ebitda_margin", "market_cap"])
```

## アクセシビリティ

### 1. キーボードナビゲーション

- Tabキーでのフォーカス移動
- 方向キーでのテーブルナビゲーション
- Enter/Spaceでのアクション実行
- Escapeでのダイアログ閉じる

### 2. スクリーンリーダー対応

```python
# アクセシビリティ名の設定
widget.setAccessibleName("スクリーニング結果テーブル")
widget.setAccessibleDescription("Rule of 40スクリーニング結果の一覧表示")

# ライブリージョンでの状態通知
status_bar.setAccessibleName("ステータス")
QAccessible.updateAccessibility(status_bar, 0, QAccessible.Event.NameChanged)
```

### 3. カラーブラインド対応

- 色だけでなくアイコンでも状態を表現
- 高コントラストテーマの提供
- カスタマイズ可能なカラースキーム

このUI仕様により、直感的で効率的なユーザー体験を提供します。