"""
Light theme stylesheet for the application
"""


def get_light_theme() -> str:
    """
    Return the light theme stylesheet

    Returns:
        str: QSS stylesheet string for light theme
    """
    return """
/* ===========================
   Light Theme Stylesheet
   =========================== */

/* Main application background */
QMainWindow, QDialog, QWidget {
    background-color: #f5f5f5;
    color: #212121;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* Group boxes */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    margin-top: 10px;
    padding: 10px;
    font-weight: bold;
    color: #212121;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #ffffff;
}

/* Push buttons */
QPushButton {
    background-color: #0d7377;
    color: #ffffff;
    border: 1px solid #0a5a5d;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #14a6ab;
    border: 1px solid #0d7377;
}

QPushButton:pressed {
    background-color: #0a5a5d;
    border: 1px solid #073f42;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    border: 1px solid #d0d0d0;
}

QPushButton:flat {
    background-color: transparent;
    border: none;
    color: #212121;
}

QPushButton:flat:hover {
    background-color: #e0e0e0;
}

/* Line edit and text edit */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    padding: 5px;
    selection-background-color: #0d7377;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0d7377;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #f5f5f5;
    color: #9e9e9e;
}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    padding: 3px;
    selection-background-color: #0d7377;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #0d7377;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #f0f0f0;
    border-left: 1px solid #d0d0d0;
    border-top-right-radius: 3px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #e0e0e0;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #f0f0f0;
    border-left: 1px solid #d0d0d0;
    border-bottom-right-radius: 3px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #e0e0e0;
}

/* Combo boxes */
QComboBox {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    padding: 5px;
    min-width: 80px;
}

QComboBox:hover {
    border: 1px solid #b0b0b0;
}

QComboBox:focus {
    border: 1px solid #0d7377;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #212121;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
    selection-background-color: #0d7377;
    selection-color: #ffffff;
    outline: none;
}

/* Check boxes */
QCheckBox {
    color: #212121;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border: 1px solid #b0b0b0;
}

QCheckBox::indicator:checked {
    background-color: #0d7377;
    border: 1px solid #0d7377;
    image: none;
}

QCheckBox::indicator:checked::after {
    content: "✓";
    color: #ffffff;
}

QCheckBox::indicator:disabled {
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
}

/* Radio buttons */
QRadioButton {
    color: #212121;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d0d0d0;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:hover {
    border: 1px solid #b0b0b0;
}

QRadioButton::indicator:checked {
    background-color: #0d7377;
    border: 1px solid #0d7377;
}

QRadioButton::indicator:checked::after {
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background-color: #ffffff;
}

/* Labels */
QLabel {
    color: #212121;
    background: transparent;
}

QLabel[class="header"] {
    font-size: 16px;
    font-weight: bold;
    color: #000000;
}

QLabel[class="subheader"] {
    font-size: 12px;
    color: #616161;
}

/* Tab widget */
QTabWidget::pane {
    border: 1px solid #d0d0d0;
    background-color: #f5f5f5;
    border-radius: 3px;
}

QTabBar::tab {
    background-color: #e0e0e0;
    color: #616161;
    border: 1px solid #d0d0d0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #f5f5f5;
    color: #212121;
    border-bottom: 2px solid #0d7377;
}

QTabBar::tab:hover:!selected {
    background-color: #d0d0d0;
}

/* Table widget */
QTableWidget, QTableView {
    background-color: #ffffff;
    alternate-background-color: #fafafa;
    color: #212121;
    gridline-color: #e0e0e0;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    selection-background-color: #0d7377;
    selection-color: #ffffff;
}

QTableWidget::item, QTableView::item {
    padding: 5px;
    border: none;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0d7377;
    color: #ffffff;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #f0f0f0;
}

QHeaderView {
    background-color: #e0e0e0;
    color: #212121;
    border: none;
}

QHeaderView::section {
    background-color: #e0e0e0;
    color: #212121;
    padding: 8px;
    border: none;
    border-right: 1px solid #d0d0d0;
    border-bottom: 1px solid #d0d0d0;
    font-weight: bold;
}

QHeaderView::section:hover {
    background-color: #d0d0d0;
}

QHeaderView::section:pressed {
    background-color: #0d7377;
    color: #ffffff;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 14px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 7px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 14px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 7px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Scroll area */
QScrollArea {
    background-color: transparent;
    border: none;
}

/* Menu bar */
QMenuBar {
    background-color: #ffffff;
    color: #212121;
    border-bottom: 1px solid #d0d0d0;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QMenuBar::item:pressed {
    background-color: #0d7377;
    color: #ffffff;
}

/* Menu */
QMenu {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
}

QMenu::item {
    padding: 5px 25px 5px 10px;
}

QMenu::item:selected {
    background-color: #0d7377;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #d0d0d0;
    margin: 5px 0;
}

/* Tool bar */
QToolBar {
    background-color: #ffffff;
    border: none;
    spacing: 3px;
    padding: 3px;
}

QToolBar::separator {
    background-color: #d0d0d0;
    width: 1px;
    margin: 5px;
}

/* Tool button */
QToolButton {
    background-color: transparent;
    color: #212121;
    border: none;
    border-radius: 3px;
    padding: 5px;
}

QToolButton:hover {
    background-color: #e0e0e0;
}

QToolButton:pressed {
    background-color: #0d7377;
    color: #ffffff;
}

/* Status bar */
QStatusBar {
    background-color: #ffffff;
    color: #212121;
    border-top: 1px solid #d0d0d0;
}

/* Progress bar */
QProgressBar {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    text-align: center;
    color: #212121;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #0d7377;
    border-radius: 2px;
}

/* Slider */
QSlider::groove:horizontal {
    background-color: #d0d0d0;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #0d7377;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #14a6ab;
}

/* Tooltip */
QToolTip {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #d0d0d0;
    padding: 5px;
    border-radius: 3px;
}

/* Splitter */
QSplitter::handle {
    background-color: #d0d0d0;
}

QSplitter::handle:hover {
    background-color: #b0b0b0;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Dialog button box */
QDialogButtonBox {
    button-layout: 0;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
}
"""
