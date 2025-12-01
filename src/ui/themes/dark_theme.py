"""
Dark theme stylesheet for the application
"""


def get_dark_theme() -> str:
    """
    Return the dark theme stylesheet

    Returns:
        str: QSS stylesheet string for dark theme
    """
    return """
/* ===========================
   Dark Theme Stylesheet
   =========================== */

/* Main application background */
QMainWindow, QDialog, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* Group boxes */
QGroupBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding: 10px;
    font-weight: bold;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #2d2d2d;
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
    background-color: #3d3d3d;
    color: #888888;
    border: 1px solid #2d2d2d;
}

QPushButton:flat {
    background-color: transparent;
    border: none;
}

QPushButton:flat:hover {
    background-color: #3d3d3d;
}

/* Line edit and text edit */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
    selection-background-color: #0d7377;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0d7377;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #252525;
    color: #888888;
}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 3px;
    selection-background-color: #0d7377;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #0d7377;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #3d3d3d;
    border-left: 1px solid #3d3d3d;
    border-top-right-radius: 3px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background-color: #4d4d4d;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #3d3d3d;
    border-left: 1px solid #3d3d3d;
    border-bottom-right-radius: 3px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #4d4d4d;
}

/* Combo boxes */
QComboBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
    min-width: 80px;
}

QComboBox:hover {
    border: 1px solid #4d4d4d;
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
    border-top: 5px solid #e0e0e0;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    selection-background-color: #0d7377;
    selection-color: #ffffff;
    outline: none;
}

/* Check boxes */
QCheckBox {
    color: #e0e0e0;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:hover {
    border: 1px solid #4d4d4d;
}

QCheckBox::indicator:checked {
    background-color: #0d7377;
    border: 1px solid #0d7377;
    image: none;
}

QCheckBox::indicator:disabled {
    background-color: #252525;
    border: 1px solid #2d2d2d;
}

/* Radio buttons */
QRadioButton {
    color: #e0e0e0;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3d3d3d;
    border-radius: 9px;
    background-color: #2d2d2d;
}

QRadioButton::indicator:hover {
    border: 1px solid #4d4d4d;
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
    color: #e0e0e0;
    background: transparent;
}

QLabel[class="header"] {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

QLabel[class="subheader"] {
    font-size: 12px;
    color: #b0b0b0;
}

/* Tab widget */
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    background-color: #1e1e1e;
    border-radius: 3px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #b0b0b0;
    border: 1px solid #3d3d3d;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #0d7377;
}

QTabBar::tab:hover:!selected {
    background-color: #3d3d3d;
}

/* Table widget */
QTableWidget, QTableView {
    background-color: #1e1e1e;
    alternate-background-color: #252525;
    color: #e0e0e0;
    gridline-color: #3d3d3d;
    border: 1px solid #3d3d3d;
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
    background-color: #2d2d2d;
}

QHeaderView {
    background-color: #2d2d2d;
    color: #ffffff;
    border: none;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 8px;
    border: none;
    border-right: 1px solid #3d3d3d;
    border-bottom: 1px solid #3d3d3d;
    font-weight: bold;
}

QHeaderView::section:hover {
    background-color: #3d3d3d;
}

QHeaderView::section:pressed {
    background-color: #0d7377;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 14px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3d3d3d;
    border-radius: 7px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4d4d4d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 14px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #3d3d3d;
    border-radius: 7px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4d4d4d;
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
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenuBar::item:pressed {
    background-color: #0d7377;
}

/* Menu */
QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
}

QMenu::item {
    padding: 5px 25px 5px 10px;
}

QMenu::item:selected {
    background-color: #0d7377;
}

QMenu::separator {
    height: 1px;
    background-color: #3d3d3d;
    margin: 5px 0;
}

/* Tool bar */
QToolBar {
    background-color: #2d2d2d;
    border: none;
    spacing: 3px;
    padding: 3px;
}

QToolBar::separator {
    background-color: #3d3d3d;
    width: 1px;
    margin: 5px;
}

/* Tool button */
QToolButton {
    background-color: transparent;
    color: #e0e0e0;
    border: none;
    border-radius: 3px;
    padding: 5px;
}

QToolButton:hover {
    background-color: #3d3d3d;
}

QToolButton:pressed {
    background-color: #0d7377;
}

/* Status bar */
QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-top: 1px solid #3d3d3d;
}

/* Progress bar */
QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    text-align: center;
    color: #e0e0e0;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #0d7377;
    border-radius: 2px;
}

/* Slider */
QSlider::groove:horizontal {
    background-color: #3d3d3d;
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
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4d4d4d;
    padding: 5px;
    border-radius: 3px;
}

/* Splitter */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:hover {
    background-color: #4d4d4d;
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
