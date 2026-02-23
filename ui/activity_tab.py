"""
活动统计Tab - Apple 设计风格
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QDateEdit,
    QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import pyqtgraph as pg
from datetime import datetime, timedelta
from collections import defaultdict

from tracker import ActivityManager
from .widgets import MetricCard, StatCard
from .styles import COLORS, CHART_STYLE
import i18n
import i18n


class ActivityTab(QWidget):
    """活动统计Tab"""
    
    app_event = pyqtSignal(dict)
    web_event = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.activity_manager = ActivityManager()
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        """设置界面"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(22)
        
        # ============ 顶部状态 ============
        top_layout = QHBoxLayout()
        top_layout.setSpacing(18)
        
        # 当前网站
        site_frame = QFrame()
        site_frame.setObjectName("card")
        site_layout = QVBoxLayout(site_frame)
        site_layout.setContentsMargins(24, 20, 24, 20)
        site_layout.setSpacing(10)
        
        site_header = QHBoxLayout()
        site_icon = QLabel("🌐")
        site_icon.setStyleSheet("font-size: 24px;")
        site_header.addWidget(site_icon)
        self.site_label = QLabel(i18n._("activity_current_browse"))
        self.site_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 12px; font-weight: 600; letter-spacing: 1px;")
        site_header.addWidget(self.site_label)
        site_header.addStretch()
        site_layout.addLayout(site_header)
        
        self.current_site = QLabel("-")
        self.current_site.setStyleSheet("color: #0a84ff; font-size: 20px; font-weight: 700;")
        site_layout.addWidget(self.current_site)
        
        self.duration_label = QLabel("⏱️ " + i18n._("activity_duration") + " -")
        self.duration_label.setStyleSheet("color: rgba(255,255,255,0.45); font-size: 13px;")
        site_layout.addWidget(self.duration_label)
        
        top_layout.addWidget(site_frame, stretch=2)
        
        # 今日摘要
        summary_frame = QFrame()
        summary_frame.setObjectName("card")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(24, 20, 24, 20)
        summary_layout.setSpacing(12)
        
        summary_header = QHBoxLayout()
        summary_icon = QLabel("📊")
        summary_icon.setStyleSheet("font-size: 24px;")
        summary_header.addWidget(summary_icon)
        self.summary_label = QLabel(i18n._("activity_today_summary"))
        self.summary_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 12px; font-weight: 600; letter-spacing: 1px;")
        summary_header.addWidget(self.summary_label)
        summary_header.addStretch()
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedWidth(115)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        summary_header.addWidget(self.date_edit)
        
        summary_layout.addLayout(summary_header)
        
        stats_row = QHBoxLayout()
        stats_row.setSpacing(30)
        
        # 使用时长
        time_box = QVBoxLayout()
        time_box.setSpacing(4)
        time_header = QHBoxLayout()
        time_header.addWidget(QLabel("⏰"))
        time_header.itemAt(0).widget().setStyleSheet("font-size: 16px;")
        self.usage_time_label = QLabel(i18n._("activity_usage_time"))
        self.usage_time_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 11px;")
        time_header.addWidget(self.usage_time_label)
        time_header.addStretch()
        time_box.addLayout(time_header)
        self.total_time = QLabel(i18n._("activity_hours_mins").format(hours=0, mins=0))
        self.total_time.setStyleSheet("color: #30d158; font-size: 18px; font-weight: 700;")
        time_box.addWidget(self.total_time)
        stats_row.addLayout(time_box)
        
        # 应用数量
        app_box = QVBoxLayout()
        app_box.setSpacing(4)
        app_header = QHBoxLayout()
        app_header.addWidget(QLabel("📱"))
        app_header.itemAt(0).widget().setStyleSheet("font-size: 16px;")
        self.app_header_label = QLabel(i18n._("activity_app_count"))
        self.app_header_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 11px;")
        app_header.addWidget(self.app_header_label)
        app_header.addStretch()
        app_box.addLayout(app_header)
        self.app_count = QLabel("0")
        self.app_count.setStyleSheet("color: #0a84ff; font-size: 18px; font-weight: 700;")
        app_box.addWidget(self.app_count)
        stats_row.addLayout(app_box)
        
        # 网站数量
        site_box = QVBoxLayout()
        site_box.setSpacing(4)
        site_header2 = QHBoxLayout()
        site_header2.addWidget(QLabel("🔗"))
        site_header2.itemAt(0).widget().setStyleSheet("font-size: 16px;")
        self.site_header_label = QLabel(i18n._("activity_site_count"))
        self.site_header_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 11px;")
        site_header2.addWidget(self.site_header_label)
        site_header2.addStretch()
        site_box.addLayout(site_header2)
        self.site_count = QLabel("0")
        self.site_count.setStyleSheet("color: #bf5af2; font-size: 18px; font-weight: 700;")
        site_box.addWidget(self.site_count)
        stats_row.addLayout(site_box)
        
        stats_row.addStretch()
        summary_layout.addLayout(stats_row)
        
        top_layout.addWidget(summary_frame, stretch=3)
        
        layout.addLayout(top_layout)
        
        # ============ 时间线直方图 ============
        timeline_frame = QFrame()
        timeline_frame.setObjectName("card")
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.setContentsMargins(24, 22, 24, 22)
        timeline_layout.setSpacing(16)
        
        timeline_header = QHBoxLayout()
        self.timeline_title = QLabel("📅 " + i18n._("activity_time_dist"))
        self.timeline_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        timeline_header.addWidget(self.timeline_title)
        timeline_header.addStretch()
        
        self.timeline_hint = QLabel(i18n._("activity_by_hour"))
        self.timeline_hint.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 12px;")
        timeline_header.addWidget(self.timeline_hint)
        
        timeline_layout.addLayout(timeline_header)
        
        self.timeline_chart = pg.PlotWidget()
        self._style_timeline_chart(self.timeline_chart)
        self.timeline_chart.setMinimumHeight(180)
        timeline_layout.addWidget(self.timeline_chart)
        
        layout.addWidget(timeline_frame)
        
        # ============ 主内容区 ============
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255,255,255,0.06); width: 1px; }")
        
        # 左侧：应用使用直方图
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        
        # 应用使用直方图
        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(24, 22, 24, 22)
        chart_layout.setSpacing(16)
        
        self.app_chart_title = QLabel("📊 " + i18n._("activity_app_ranking"))
        self.app_chart_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        chart_layout.addWidget(self.app_chart_title)
        
        self.app_chart = pg.PlotWidget()
        self._style_bar_chart(self.app_chart)
        self.app_chart.setMinimumHeight(250)
        chart_layout.addWidget(self.app_chart)
        
        left_layout.addWidget(chart_frame)
        
        splitter.addWidget(left)
        
        # 右侧：网站访问直方图
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(18)
        
        # 网站访问直方图
        web_chart_frame = QFrame()
        web_chart_frame.setObjectName("card")
        web_chart_layout = QVBoxLayout(web_chart_frame)
        web_chart_layout.setContentsMargins(24, 22, 24, 22)
        web_chart_layout.setSpacing(16)
        
        self.web_chart_title = QLabel("🌐 " + i18n._("activity_site_ranking"))
        self.web_chart_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        web_chart_layout.addWidget(self.web_chart_title)
        
        self.web_chart = pg.PlotWidget()
        self._style_bar_chart(self.web_chart)
        self.web_chart.setMinimumHeight(250)
        web_chart_layout.addWidget(self.web_chart)
        
        right_layout.addWidget(web_chart_frame)
        
        splitter.addWidget(right)
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter, stretch=1)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _style_timeline_chart(self, chart):
        """时间线直方图样式"""
        chart.setBackground('#1c1c1e')
        chart.getAxis('left').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('bottom').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('left').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.getAxis('bottom').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.showGrid(x=False, y=True, alpha=0.05)
        chart.setMouseEnabled(x=False, y=False)
        
        # 设置X轴为小时
        hours = [(i, f"{i}:00") for i in range(0, 24, 2)]
        chart.getAxis('bottom').setTicks([hours])
        chart.setXRange(-0.5, 23.5)
    
    def _style_bar_chart(self, chart):
        """条形图样式"""
        chart.setBackground('#1c1c1e')
        chart.getAxis('left').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('bottom').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('left').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.getAxis('bottom').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.showGrid(x=False, y=True, alpha=0.05)
        chart.setMouseEnabled(x=False, y=False)
    
    def _setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_tracking)
        self.update_timer.start(1000)
    
    def _on_date_changed(self, date):
        self._refresh_data()
    
    def _format_duration(self, seconds: float) -> str:
        return self.activity_manager.format_duration(seconds)
    
    def _update_tracking(self):
        try:
            result = self.activity_manager.update()
            
            current_app = result.get('current_app')
            if current_app:
                self.duration_label.setText(
                    f"⏱️ {i18n._('activity_duration')} {self._format_duration(current_app.get('duration', 0))}"
                )
            else:
                self.duration_label.setText("⏱️ " + i18n._("activity_duration") + " -")
            
            current_site = result.get('current_site')
            if current_site:
                self.current_site.setText(current_site.get('site_title', '-'))
            else:
                self.current_site.setText("-")
            
            if result.get('app_event'):
                self.app_event.emit(result['app_event'])
            if result.get('site_event'):
                self.web_event.emit(result['site_event'])
            
            if not hasattr(self, '_counter'):
                self._counter = 0
            self._counter += 1
            if self._counter >= 5:
                self._counter = 0
                self._refresh_data()
        
        except Exception as e:
            print(f"追踪错误: {e}")
    
    def _refresh_data(self):
        try:
            is_today = self.date_edit.date().toPyDate() == datetime.now().date()
            if is_today:
                self._refresh_today()
        except Exception as e:
            print(f"刷新错误: {e}")
    
    def _refresh_today(self):
        summary = self.activity_manager.get_summary()
        total = summary['total_app_time']
        hours = int(total // 3600)
        mins = int((total % 3600) // 60)
        fmt = i18n._("activity_hours_mins")
        self.total_time.setText(fmt.format(hours=hours, mins=mins))
        self.app_count.setText(str(summary['app_count']))
        self.site_count.setText(str(summary['site_count']))
        
        # 更新应用使用直方图
        app_usage = self.activity_manager.get_app_usage_sorted()
        self._update_app_chart(app_usage[:10])
        
        # 更新网站访问直方图
        site_stats = self.activity_manager.get_site_visits_sorted()
        self._update_web_chart(site_stats[:10])
        
        # 更新时间线直方图
        self._update_timeline_chart()
    
    def _update_app_chart(self, data):
        """更新应用使用直方图"""
        self.app_chart.clear()
        if not data:
            return
        
        colors = ['#0a84ff', '#30d158', '#bf5af2', '#ff9f0a', '#ff453a', 
                  '#64d2ff', '#5e5ce6', '#ff375f', '#ffd60a', '#ac8e68']
        
        # 水平条形图
        y = list(range(len(data)))
        widths = [d[1] / 60 for d in data]  # 转换为分钟
        
        for i, (name, duration) in enumerate(data):
            bar = pg.BarGraphItem(
                x0=0, y=[len(data) - 1 - i], height=0.6, width=duration / 60,
                brush=pg.mkBrush(colors[i % len(colors)])
            )
            self.app_chart.addItem(bar)
        
        # 设置Y轴标签
        labels = [(len(data) - 1 - i, data[i][0][:12]) for i in range(len(data))]
        self.app_chart.getAxis('left').setTicks([labels])
        
        # 设置X轴标签（分钟）
        max_mins = max(widths) if widths else 1
        self.app_chart.setXRange(0, max_mins * 1.1)
        self.app_chart.setYRange(-0.5, len(data) - 0.5)
        self.app_chart.setLabel('bottom', i18n._('activity_usage_mins'))
    
    def _update_web_chart(self, data):
        """更新网站访问直方图"""
        self.web_chart.clear()
        if not data:
            return
        
        colors = ['#0a84ff', '#30d158', '#bf5af2', '#ff9f0a', '#ff453a', 
                  '#64d2ff', '#5e5ce6', '#ff375f', '#ffd60a', '#ac8e68']
        
        # 水平条形图
        for i, (name, duration) in enumerate(data):
            bar = pg.BarGraphItem(
                x0=0, y=[len(data) - 1 - i], height=0.6, width=duration / 60,
                brush=pg.mkBrush(colors[i % len(colors)])
            )
            self.web_chart.addItem(bar)
        
        # 设置Y轴标签
        labels = [(len(data) - 1 - i, data[i][0][:15]) for i in range(len(data))]
        self.web_chart.getAxis('left').setTicks([labels])
        
        widths = [d[1] / 60 for d in data]
        max_mins = max(widths) if widths else 1
        self.web_chart.setXRange(0, max_mins * 1.1)
        self.web_chart.setYRange(-0.5, len(data) - 0.5)
        self.web_chart.setLabel('bottom', i18n._('activity_visit_mins'))
    
    def _update_timeline_chart(self):
        """更新时间线直方图 - 按小时统计使用时间"""
        self.timeline_chart.clear()
        
        # 获取活动日志并按小时统计
        hourly_usage = defaultdict(float)
        
        # 从 activity_manager 获取应用活动日志
        app_log = self.activity_manager.app_tracker.get_activity_log()
        
        for entry in app_log:
            try:
                ts = entry.get('timestamp', '')
                duration = entry.get('duration', 0)
                if ts and duration > 0:
                    dt = datetime.fromisoformat(ts)
                    if dt.date() == datetime.now().date():
                        hour = dt.hour
                        hourly_usage[hour] += duration / 60  # 转换为分钟
            except:
                pass
        
        # 创建24小时的数据
        hours = list(range(24))
        values = [hourly_usage.get(h, 0) for h in hours]
        
        # 绘制直方图
        colors = []
        for h in hours:
            if values[h] > 0:
                # 根据使用量设置颜色深浅
                intensity = min(values[h] / 60, 1)  # 最多60分钟满色
                colors.append(pg.mkBrush(10, 132, 255, int(100 + 155 * intensity)))
            else:
                colors.append(pg.mkBrush(255, 255, 255, 20))
        
        bg = pg.BarGraphItem(
            x=hours, height=values, width=0.8,
            brushes=colors
        )
        self.timeline_chart.addItem(bg)
        
        # 添加当前时间指示线
        current_hour = datetime.now().hour
        line = pg.InfiniteLine(pos=current_hour, angle=90, 
                               pen=pg.mkPen(color='#ff453a', width=2, style=Qt.DashLine))
        self.timeline_chart.addItem(line)
        
        max_val = max(values) if max(values) > 0 else 60
        self.timeline_chart.setYRange(0, max_val * 1.1)
        self.timeline_chart.setLabel('left', i18n._('activity_timeline_ylabel'))
    
    def retranslate_ui(self):
        """语言切换后刷新本 Tab 文字"""
        self.site_label.setText(i18n._("activity_current_browse"))
        result = self.activity_manager.update()
        current_app = result.get("current_app")
        if current_app:
            self.duration_label.setText(f"⏱️ {i18n._('activity_duration')} {self._format_duration(current_app.get('duration', 0))}")
        else:
            self.duration_label.setText("⏱️ " + i18n._("activity_duration") + " -")
        self.summary_label.setText(i18n._("activity_today_summary"))
        self.usage_time_label.setText(i18n._("activity_usage_time"))
        self.app_header_label.setText(i18n._("activity_app_count"))
        self.site_header_label.setText(i18n._("activity_site_count"))
        self.timeline_title.setText("📅 " + i18n._("activity_time_dist"))
        self.timeline_hint.setText(i18n._("activity_by_hour"))
        self.app_chart_title.setText("📊 " + i18n._("activity_app_ranking"))
        self.web_chart_title.setText("🌐 " + i18n._("activity_site_ranking"))
        summary = self.activity_manager.get_summary()
        total = summary["total_app_time"]
        hours = int(total // 3600)
        mins = int((total % 3600) // 60)
        self.total_time.setText(i18n._("activity_hours_mins").format(hours=hours, mins=mins))
        self.app_chart.setLabel("bottom", i18n._("activity_usage_mins"))
        self.web_chart.setLabel("bottom", i18n._("activity_visit_mins"))
        self.timeline_chart.setLabel("left", i18n._("activity_timeline_ylabel"))
    
    def start_tracking(self):
        if not self.update_timer.isActive():
            self.update_timer.start()
    
    def stop_tracking(self):
        self.update_timer.stop()
    
    def get_activity_manager(self):
        return self.activity_manager
