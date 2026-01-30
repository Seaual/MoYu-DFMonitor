"""
主窗口 - 摸鱼了么
Apple 设计风格 - 无边框窗口
"""
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar, QAction, QMenu,
    QSystemTrayIcon, QMessageBox, QApplication, QFrame,
    QPushButton, QToolButton, QSizeGrip
)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint, QRect
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QLinearGradient, QCursor

from .monitor_tab import MonitorTab
from .activity_tab import ActivityTab
from .footprint_tab import FootprintTab
from .styles import DARK_STYLE, COLORS
from utils import DataLogger, AutoStart


class MainWindow(QMainWindow):
    """主窗口 - 摸鱼了么"""
    
    APP_NAME = "摸鱼了么"
    APP_SUBTITLE = "PC数字足迹检测"
    
    def __init__(self):
        super().__init__()
        
        # 无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.setWindowTitle(f"{self.APP_NAME} - {self.APP_SUBTITLE}")
        self.setMinimumSize(1200, 800)
        
        # 应用样式
        self.setStyleSheet(DARK_STYLE)
        
        # 隐藏菜单栏
        self.menuBar().hide()
        
        # 初始化
        self.data_logger = DataLogger()
        self.auto_start = AutoStart()
        
        # 窗口拖动相关
        self._drag_pos = None
        self._is_maximized = False
        
        self._setup_ui()
        self._setup_tray()
        self._setup_connections()
        self._update_status()
    
    def _setup_ui(self):
        """设置界面"""
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet("""
            #centralWidget {
                background-color: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 10px;
            }
        """)
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ============ 自定义标题栏 ============
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(42)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("""
            #titleBar {
                background-color: #1c1c1e;
                border: none;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)
        title_layout.setSpacing(8)
        
        # Mac风格窗口控制按钮（左侧）- 红黄绿三色圆点
        # 关闭按钮 - 红色
        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(14, 14)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #ff3b30;
            }
        """)
        self.btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_close.setToolTip("关闭")
        self.btn_close.clicked.connect(self._quit_app)
        title_layout.addWidget(self.btn_close)
        
        # 最小化按钮 - 黄色
        self.btn_minimize = QPushButton()
        self.btn_minimize.setFixedSize(14, 14)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: #febc2e;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #f5a623;
            }
        """)
        self.btn_minimize.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_minimize.setToolTip("最小化")
        self.btn_minimize.clicked.connect(self._minimize_to_tray)
        title_layout.addWidget(self.btn_minimize)
        
        # 最大化按钮 - 绿色
        self.btn_maximize = QPushButton()
        self.btn_maximize.setFixedSize(14, 14)
        self.btn_maximize.setStyleSheet("""
            QPushButton {
                background-color: #28c840;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #1db954;
            }
        """)
        self.btn_maximize.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_maximize.setToolTip("最大化")
        self.btn_maximize.clicked.connect(self._toggle_maximize)
        title_layout.addWidget(self.btn_maximize)
        
        title_layout.addStretch()
        
        # 标题文字（居中）
        title_label = QLabel(f"🐟 {self.APP_NAME}——{self.APP_SUBTITLE}")
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 设置按钮（右侧）
        self.settings_btn = QPushButton("设置")
        self.settings_btn.setFixedHeight(26)
        self.settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                border-radius: 5px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #ffffff;
            }
        """)
        self.settings_btn.clicked.connect(self._show_settings_menu)
        title_layout.addWidget(self.settings_btn)
        
        main_layout.addWidget(self.title_bar)
        
        # ============ Tab控件 ============
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # 创建Tab（数字足迹放在第一位）
        self.monitor_tab = MonitorTab()
        self.footprint_tab = FootprintTab(self.monitor_tab.monitor)
        self.activity_tab = ActivityTab()
        
        # 添加Tab - 数字足迹优先
        self.tab_widget.addTab(self.footprint_tab, "🌍 数字足迹")
        self.tab_widget.addTab(self.monitor_tab, "💻 系统监控")
        self.tab_widget.addTab(self.activity_tab, "📈 活动统计")
        
        main_layout.addWidget(self.tab_widget)
        
        # ============ 状态栏 ============
        status_frame = QFrame()
        status_frame.setFixedHeight(30)
        status_frame.setObjectName("statusFrame")
        status_frame.setStyleSheet("""
            #statusFrame {
                background-color: #252527;
                border: none;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(16, 0, 16, 0)
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 11px;")
        status_layout.addWidget(version_label)
        
        status_layout.addStretch()
        
        self.autostart_label = QLabel()
        self.autostart_label.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(self.autostart_label)
        
        main_layout.addWidget(status_frame)
        
        # 创建设置菜单
        self._create_settings_menu()
        
        # 窗口大小调整手柄
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent;")
    
    def _create_settings_menu(self):
        """创建设置菜单"""
        self.settings_menu = QMenu(self)
        self.settings_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(44, 44, 46, 0.98);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 10px 24px 10px 16px;
                border-radius: 8px;
                margin: 2px 4px;
                color: #ffffff;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #0a84ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.1);
                margin: 6px 12px;
            }
        """)
        
        # 开机自启动
        self.autostart_action = QAction("🚀 开机自启动", self)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(self.auto_start.is_enabled())
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.settings_menu.addAction(self.autostart_action)
        
        self.settings_menu.addSeparator()
        
        # 导出数据
        export_action = QAction("📁 导出数据", self)
        export_action.triggered.connect(self._export_data)
        self.settings_menu.addAction(export_action)
        
        self.settings_menu.addSeparator()
        
        # 关于
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self._show_about)
        self.settings_menu.addAction(about_action)
        
        self.settings_menu.addSeparator()
        
        # 退出
        exit_action = QAction("🚪 退出程序", self)
        exit_action.triggered.connect(self._quit_app)
        self.settings_menu.addAction(exit_action)
    
    def _show_settings_menu(self):
        """显示设置菜单"""
        btn_pos = self.settings_btn.mapToGlobal(QPoint(0, self.settings_btn.height() + 4))
        # 右对齐菜单
        menu_width = 180
        btn_pos.setX(btn_pos.x() - menu_width + self.settings_btn.width())
        self.settings_menu.exec_(btn_pos)
    
    def _minimize_to_tray(self):
        """最小化到托盘"""
        self.hide()
    
    def _toggle_maximize(self):
        """切换最大化状态"""
        if self._is_maximized:
            self.showNormal()
            self._is_maximized = False
        else:
            self.showMaximized()
            self._is_maximized = True
    
    def _create_tray_icon(self) -> QIcon:
        """创建托盘图标"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 64, 64)
        gradient.setColorAt(0, QColor("#0a84ff"))
        gradient.setColorAt(1, QColor("#bf5af2"))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
        
        painter.setPen(QColor("white"))
        font = QFont("Segoe UI Emoji", 24)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "🐟")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._create_tray_icon())
        self.tray_icon.setToolTip(f"{self.APP_NAME} - {self.APP_SUBTITLE}")
        
        tray_menu = QMenu()
        tray_menu.setStyleSheet(DARK_STYLE)
        
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        self.tray_icon.show()
    
    def _setup_connections(self):
        """设置信号连接"""
        self.monitor_tab.record_requested.connect(self._on_system_record)
        self.activity_tab.app_event.connect(self._on_app_event)
        self.activity_tab.web_event.connect(self._on_web_event)
    
    def _on_system_record(self, snapshot):
        self.data_logger.log_system_snapshot(snapshot)
    
    def _on_app_event(self, event):
        self.data_logger.log_app_event(event)
    
    def _on_web_event(self, event):
        self.data_logger.log_web_event(event)
    
    def _update_status(self):
        if self.auto_start.is_enabled():
            self.autostart_label.setText("● 开机自启动已启用")
            self.autostart_label.setStyleSheet("color: #30d158; font-size: 11px;")
        else:
            self.autostart_label.setText("○ 开机自启动未启用")
            self.autostart_label.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px;")
    
    def _toggle_autostart(self, checked):
        if checked:
            if self.auto_start.enable():
                pass
            else:
                self.autostart_action.setChecked(False)
                QMessageBox.warning(self, "提示", "启用开机自启动失败")
        else:
            self.auto_start.disable()
        self._update_status()
    
    def _export_data(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("导出数据")
        msg.setText(f"数据已保存至:\n\n{self.data_logger.data_dir.absolute()}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(DARK_STYLE)
        msg.exec_()
    
    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(f"关于 {self.APP_NAME}")
        msg.setText(
            f"<div style='text-align: center;'>"
            f"<h2 style='color: #0a84ff; margin-bottom: 4px;'>🐟 {self.APP_NAME}</h2>"
            f"<p style='color: rgba(255,255,255,0.6); margin-top: 0;'>{self.APP_SUBTITLE}</p>"
            f"</div>"
            f"<hr style='border-color: rgba(255,255,255,0.1);'>"
            f"<p style='color: rgba(255,255,255,0.8); line-height: 1.6;'>"
            f"一款帮助你了解个人电脑资源消耗的工具。<br><br>"
            f"监测 CPU、内存、GPU 使用率，追踪软件使用时长，"
            f"计算能耗与碳排放，全面量化你的数字足迹。</p>"
            f"<hr style='border-color: rgba(255,255,255,0.1);'>"
            f"<p style='color: rgba(255,255,255,0.6); font-size: 12px;'>"
            f"📚 参考文献:</p>"
            f"<p style='color: #0a84ff; font-size: 11px;'>"
            f"<a href='https://doi.org/10.1016/j.compag.2024.109875' style='color: #0a84ff;'>"
            f"DOI: 10.1016/j.compag.2024.109875</a><br>"
            f"<a href='https://doi.org/10.1016/j.compag.2024.109206' style='color: #0a84ff;'>"
            f"DOI: 10.1016/j.compag.2024.109206</a></p>"
            f"<p style='color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 12px;'>"
            f"基于 Digitization Footprint (DF-LCA) 框架开发<br>"
            f"Version 1.0.0</p>"
        )
        msg.setStyleSheet(DARK_STYLE + """
            QMessageBox {
                background-color: #1c1c1e;
            }
            QMessageBox QLabel {
                color: #ffffff;
                min-width: 360px;
            }
        """)
        msg.exec_()
    
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    
    def show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self._is_maximized = False
    
    def _quit_app(self):
        self.monitor_tab.stop_monitoring()
        self.activity_tab.stop_tracking()
        self.footprint_tab.stop_monitoring()
        self.data_logger.close()
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    # ============ 无边框窗口拖动支持 ============
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 只有在标题栏区域才能拖动
            if self.title_bar.geometry().contains(event.pos()):
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            if self._is_maximized:
                # 从最大化状态拖动时，先还原窗口
                self.showNormal()
                self._is_maximized = False
                # 调整拖动位置
                self._drag_pos = QPoint(self.width() // 2, 20)
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    
    def mouseDoubleClickEvent(self, event):
        if self.title_bar.geometry().contains(event.pos()):
            self._toggle_maximize()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 调整大小手柄位置
        self.size_grip.move(self.width() - 16, self.height() - 16)
