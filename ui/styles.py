"""
全局样式定义 - Apple Liquid Glass 风格
灵感来源: macOS 2025 设计语言
"""

# 颜色定义 - 苹果风格柔和色彩
COLORS = {
    # 背景色 - 深邃但不死板
    'bg_primary': '#1c1c1e',        # 主背景
    'bg_secondary': '#2c2c2e',      # 次级背景
    'bg_tertiary': '#3a3a3c',       # 第三级背景
    'bg_glass': 'rgba(44, 44, 46, 0.8)',  # 玻璃效果背景
    
    # 强调色 - 苹果风格渐变
    'accent_blue': '#0a84ff',       # 苹果蓝
    'accent_green': '#30d158',      # 苹果绿
    'accent_orange': '#ff9f0a',     # 苹果橙
    'accent_red': '#ff453a',        # 苹果红
    'accent_purple': '#bf5af2',     # 苹果紫
    'accent_pink': '#ff375f',       # 苹果粉
    'accent_teal': '#64d2ff',       # 苹果青
    'accent_indigo': '#5e5ce6',     # 苹果靛蓝
    
    # 文字色
    'text_primary': '#ffffff',
    'text_secondary': 'rgba(255, 255, 255, 0.7)',
    'text_tertiary': 'rgba(255, 255, 255, 0.5)',
    
    # 边框和分隔
    'border': 'rgba(255, 255, 255, 0.1)',
    'separator': 'rgba(255, 255, 255, 0.06)',
}

# 全局样式表 - Apple 设计风格
DARK_STYLE = """
/* ==================== 全局基础 ==================== */
QMainWindow, QWidget {
    background-color: #1c1c1e;
    color: #ffffff;
    font-family: "SF Pro Display", "PingFang SC", "Microsoft YaHei UI", -apple-system, sans-serif;
    font-size: 13px;
}

/* ==================== 菜单栏 - 极简风格 ==================== */
QMenuBar {
    background-color: transparent;
    border: none;
    padding: 8px 16px;
    spacing: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 16px;
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.85);
}

QMenuBar::item:selected {
    background-color: rgba(255, 255, 255, 0.1);
}

QMenu {
    background-color: rgba(44, 44, 46, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 20px;
    border-radius: 8px;
    margin: 2px 4px;
}

QMenu::item:selected {
    background-color: #0a84ff;
}

/* ==================== Tab控件 - 简洁高亮风格 ==================== */
QTabWidget {
    background-color: #1c1c1e;
    border: none;
    outline: none;
}

QTabWidget::pane {
    background-color: #1c1c1e;
    border: none;
    border-top: none;
    top: 0;
    outline: none;
}

QTabWidget::tab-bar {
    left: 12px;
    border: none;
}

QTabBar {
    background-color: #1c1c1e;
    border: none;
    outline: none;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background-color: transparent;
    color: rgba(255, 255, 255, 0.5);
    padding: 10px 20px;
    margin-right: 4px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: transparent;
    color: #0a84ff;
    border-bottom: 2px solid #0a84ff;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    color: rgba(255, 255, 255, 0.85);
}

/* ==================== 卡片/Frame - 玻璃形态 ==================== */
QFrame#card {
    background-color: rgba(44, 44, 46, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}

QFrame#card:hover {
    background-color: rgba(44, 44, 46, 0.7);
    border-color: rgba(255, 255, 255, 0.12);
}

QGroupBox {
    background-color: rgba(44, 44, 46, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    margin-top: 20px;
    padding: 20px;
    padding-top: 36px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    top: 10px;
    color: rgba(255, 255, 255, 0.7);
    background-color: transparent;
    padding: 0 8px;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ==================== 按钮 - 圆润现代 ==================== */
QPushButton {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.15);
}

QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.08);
}

QPushButton:checked {
    background-color: #0a84ff;
}

QPushButton#primaryButton {
    background-color: #0a84ff;
}

QPushButton#primaryButton:hover {
    background-color: #409cff;
}

QPushButton#accentButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #bf5af2, stop:1 #0a84ff);
}

/* ==================== 进度条 - 渐变填充 ==================== */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0a84ff, stop:0.5 #5e5ce6, stop:1 #bf5af2);
    border-radius: 6px;
}

/* ==================== 表格 - 简洁现代 ==================== */
QTableWidget {
    background-color: rgba(44, 44, 46, 0.4);
    border: none;
    border-radius: 12px;
    gridline-color: transparent;
    selection-background-color: rgba(10, 132, 255, 0.3);
}

QTableWidget::item {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

QTableWidget::item:selected {
    background-color: rgba(10, 132, 255, 0.2);
}

QHeaderView::section {
    background-color: transparent;
    color: rgba(255, 255, 255, 0.5);
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QTableCornerButton::section {
    background-color: transparent;
    border: none;
}

/* ==================== 滚动条 - 极简隐藏式 ==================== */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-width: 40px;
}

/* ==================== 输入控件 ==================== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: #ffffff;
    selection-background-color: #0a84ff;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #0a84ff;
    background-color: rgba(255, 255, 255, 0.1);
}

QComboBox {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: #ffffff;
    min-width: 100px;
}

QComboBox:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid rgba(255, 255, 255, 0.5);
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: rgba(44, 44, 46, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 6px;
    selection-background-color: #0a84ff;
}

QDateEdit {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: #ffffff;
}

/* ==================== 状态栏 ==================== */
QStatusBar {
    background-color: rgba(28, 28, 30, 0.8);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.5);
    padding: 8px 16px;
    font-size: 12px;
}

/* ==================== 标签 ==================== */
QLabel {
    color: #ffffff;
}

QLabel#subtitle {
    color: rgba(255, 255, 255, 0.5);
    font-size: 12px;
}

QLabel#accent {
    color: #0a84ff;
}

/* ==================== 分隔线 ==================== */
QFrame#separator {
    background-color: rgba(255, 255, 255, 0.06);
    max-height: 1px;
}

/* ==================== 工具提示 ==================== */
QToolTip {
    background-color: rgba(60, 60, 62, 0.95);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}

/* ==================== 滑块 ==================== */
QSlider::groove:horizontal {
    background-color: rgba(255, 255, 255, 0.1);
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #ffffff;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0a84ff, stop:1 #5e5ce6);
    border-radius: 2px;
}
"""

# 图表样式配置
CHART_STYLE = {
    'background': '#1c1c1e',
    'foreground': '#ffffff',
    'grid_color': 'rgba(255, 255, 255, 0.06)',
    'axis_color': 'rgba(255, 255, 255, 0.4)',
    'colors': ['#0a84ff', '#30d158', '#bf5af2', '#ff9f0a', '#ff453a', '#64d2ff'],
}

# 渐变色定义
GRADIENTS = {
    'blue_purple': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a84ff, stop:1 #bf5af2)',
    'green_teal': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #30d158, stop:1 #64d2ff)',
    'orange_red': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff9f0a, stop:1 #ff453a)',
    'purple_pink': 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #bf5af2, stop:1 #ff375f)',
}
