"""
系统监控Tab - Apple 设计风格
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import pyqtgraph as pg
from collections import deque

from monitor import SystemMonitor
from .widgets import CircularProgress, MetricCard, StatCard
from .styles import COLORS, CHART_STYLE
import i18n


class MonitorTab(QWidget):
    """系统监控Tab"""
    
    record_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.monitor = SystemMonitor()
        self.is_recording = False
        
        self.history_length = 60
        self.cpu_history = deque(maxlen=self.history_length)
        self.memory_history = deque(maxlen=self.history_length)
        self.gpu_history = deque(maxlen=self.history_length)
        self.time_history = deque(maxlen=self.history_length)
        
        self._setup_ui()
        self._setup_chart()
        self._setup_timer()
    
    def _setup_ui(self):
        """设置界面"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)
        
        # ============ 圆形仪表盘 ============
        gauges_frame = QFrame()
        gauges_frame.setObjectName("card")
        gauges_layout = QHBoxLayout(gauges_frame)
        gauges_layout.setContentsMargins(48, 36, 48, 36)
        gauges_layout.setSpacing(60)
        
        self.cpu_gauge = CircularProgress("🖥️ " + i18n._("monitor_cpu"), 120)
        self.cpu_gauge.set_colors("#0a84ff", "#5e5ce6")
        gauges_layout.addWidget(self.cpu_gauge, alignment=Qt.AlignCenter)
        
        self.memory_gauge = CircularProgress("💾 " + i18n._("monitor_memory"), 120)
        self.memory_gauge.set_colors("#30d158", "#64d2ff")
        gauges_layout.addWidget(self.memory_gauge, alignment=Qt.AlignCenter)
        
        self.gpu_gauge = CircularProgress("🎮 " + i18n._("monitor_gpu"), 120)
        self.gpu_gauge.set_colors("#bf5af2", "#ff375f")
        gauges_layout.addWidget(self.gpu_gauge, alignment=Qt.AlignCenter)
        
        self.gpu_mem_gauge = CircularProgress("📦 " + i18n._("monitor_vram"), 120)
        self.gpu_mem_gauge.set_colors("#ff9f0a", "#ff453a")
        gauges_layout.addWidget(self.gpu_mem_gauge, alignment=Qt.AlignCenter)
        
        layout.addWidget(gauges_frame)
        
        # ============ 图表和统计 ============
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(18)
        
        # 趋势图
        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(24, 22, 24, 22)
        chart_layout.setSpacing(16)
        
        chart_header = QHBoxLayout()
        self.chart_title = QLabel("📈 " + i18n._("monitor_trend"))
        self.chart_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        chart_header.addWidget(self.chart_title)
        chart_header.addStretch()
        
        legend = QHBoxLayout()
        legend.setSpacing(18)
        self.legend_cpu = QLabel("🔵 " + i18n._("monitor_legend_cpu"))
        self.legend_cpu.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend.addWidget(self.legend_cpu, alignment=Qt.AlignRight)
        self.legend_mem = QLabel("🟢 " + i18n._("monitor_legend_mem"))
        self.legend_mem.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend.addWidget(self.legend_mem)
        self.legend_gpu = QLabel("🟣 " + i18n._("monitor_legend_gpu"))
        self.legend_gpu.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend.addWidget(self.legend_gpu)
        chart_header.addLayout(legend)
        
        chart_layout.addLayout(chart_header)
        
        self.plot_widget = pg.PlotWidget()
        self._style_chart(self.plot_widget)
        chart_layout.addWidget(self.plot_widget)
        
        middle_layout.addWidget(chart_frame, stretch=3)
        
        # 统计卡片
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(14)
        
        self.freq_card = StatCard(i18n._("monitor_freq"), "-", "⚡")
        stats_layout.addWidget(self.freq_card)
        
        self.mem_card = StatCard(i18n._("monitor_mem_use"), "-", "💾")
        stats_layout.addWidget(self.mem_card)
        
        self.disk_read = StatCard(i18n._("monitor_disk_read"), "-", "📖")
        stats_layout.addWidget(self.disk_read)
        
        self.disk_write = StatCard(i18n._("monitor_disk_write"), "-", "✏️")
        stats_layout.addWidget(self.disk_write)
        
        self.net_up = StatCard(i18n._("monitor_net_up"), "-", "📤")
        stats_layout.addWidget(self.net_up)
        
        self.net_down = StatCard(i18n._("monitor_net_down"), "-", "📥")
        stats_layout.addWidget(self.net_down)
        
        stats_layout.addStretch()
        
        stats_scroll = QScrollArea()
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        stats_scroll.setWidget(stats_widget)
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setFixedWidth(220)
        stats_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        middle_layout.addWidget(stats_scroll)
        
        layout.addLayout(middle_layout, stretch=1)
        
        # ============ 控制栏 ============
        control_frame = QFrame()
        control_frame.setObjectName("card")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(24, 16, 24, 16)
        
        # GPU状态
        self.gpu_status = QLabel()
        if self.monitor.gpu_monitor.is_available():
            self.gpu_status.setText(i18n._("monitor_gpu_ok"))
            self.gpu_status.setStyleSheet("color: #30d158; font-size: 13px; font-weight: 500;")
        else:
            self.gpu_status.setText(i18n._("monitor_gpu_none"))
            self.gpu_status.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 13px;")
        control_layout.addWidget(self.gpu_status)
        
        control_layout.addStretch()
        
        self.interval_label = QLabel("⏱️ " + i18n._("monitor_interval"))
        self.interval_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 13px;")
        control_layout.addWidget(self.interval_label)
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([i18n._("monitor_interval_1"), i18n._("monitor_interval_2"), i18n._("monitor_interval_5")])
        self.interval_combo.setFixedWidth(90)
        self.interval_combo.currentIndexChanged.connect(self._on_interval_changed)
        control_layout.addWidget(self.interval_combo)
        
        control_layout.addSpacing(20)
        
        self.record_btn = QPushButton(i18n._("monitor_record_start"))
        self.record_btn.setCheckable(True)
        self.record_btn.setFixedWidth(130)
        self.record_btn.clicked.connect(self._on_record_clicked)
        control_layout.addWidget(self.record_btn)
        
        layout.addWidget(control_frame)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _style_chart(self, chart):
        chart.setBackground('#1c1c1e')
        chart.getAxis('left').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('bottom').setPen(pg.mkPen(color=(255, 255, 255, 50)))
        chart.getAxis('left').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.getAxis('bottom').setTextPen(pg.mkPen(color=(255, 255, 255, 100)))
        chart.setYRange(0, 100)
        chart.showGrid(x=True, y=True, alpha=0.05)
    
    def _setup_chart(self):
        self.cpu_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#0a84ff', width=2),
            fillLevel=0,
            fillBrush=pg.mkBrush(color=(10, 132, 255, 25))
        )
        self.memory_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#30d158', width=2),
            fillLevel=0,
            fillBrush=pg.mkBrush(color=(48, 209, 88, 25))
        )
        self.gpu_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#bf5af2', width=2),
            fillLevel=0,
            fillBrush=pg.mkBrush(color=(191, 90, 242, 25))
        )
    
    def _setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)
    
    def _on_interval_changed(self, index):
        intervals = [1000, 2000, 5000]
        self.update_timer.setInterval(intervals[index])
    
    def _on_record_clicked(self, checked):
        self.is_recording = checked
        if checked:
            self.record_btn.setText(i18n._("monitor_record_stop"))
            self.record_btn.setStyleSheet("background-color: #ff453a;")
        else:
            self.record_btn.setText(i18n._("monitor_record_start"))
            self.record_btn.setStyleSheet("")
    
    def retranslate_ui(self):
        """语言切换后刷新本 Tab 文字"""
        self.cpu_gauge.title = "🖥️ " + i18n._("monitor_cpu")
        self.cpu_gauge.update()
        self.memory_gauge.title = "💾 " + i18n._("monitor_memory")
        self.memory_gauge.update()
        self.gpu_gauge.title = "🎮 " + i18n._("monitor_gpu")
        self.gpu_gauge.update()
        self.gpu_mem_gauge.title = "📦 " + i18n._("monitor_vram")
        self.gpu_mem_gauge.update()
        self.chart_title.setText("📈 " + i18n._("monitor_trend"))
        self.legend_cpu.setText("🔵 " + i18n._("monitor_legend_cpu"))
        self.legend_mem.setText("🟢 " + i18n._("monitor_legend_mem"))
        self.legend_gpu.setText("🟣 " + i18n._("monitor_legend_gpu"))
        self.freq_card.set_title(i18n._("monitor_freq"))
        self.mem_card.set_title(i18n._("monitor_mem_use"))
        self.disk_read.set_title(i18n._("monitor_disk_read"))
        self.disk_write.set_title(i18n._("monitor_disk_write"))
        self.net_up.set_title(i18n._("monitor_net_up"))
        self.net_down.set_title(i18n._("monitor_net_down"))
        self.gpu_status.setText(i18n._("monitor_gpu_ok") if self.monitor.gpu_monitor.is_available() else i18n._("monitor_gpu_none"))
        self.interval_label.setText("⏱️ " + i18n._("monitor_interval"))
        self.interval_combo.blockSignals(True)
        self.interval_combo.clear()
        self.interval_combo.addItems([i18n._("monitor_interval_1"), i18n._("monitor_interval_2"), i18n._("monitor_interval_5")])
        self.interval_combo.blockSignals(False)
        self.record_btn.setText(i18n._("monitor_record_stop") if self.is_recording else i18n._("monitor_record_start"))
    
    def _update_data(self):
        try:
            snapshot = self.monitor.get_snapshot()
            
            cpu = snapshot['cpu_percent']
            mem = snapshot['memory_percent']
            gpu = snapshot['gpu_percent']
            gpu_mem = snapshot['gpu_memory_percent']
            
            self.cpu_gauge.set_value(cpu)
            self.memory_gauge.set_value(mem)
            self.gpu_gauge.set_value(gpu)
            self.gpu_mem_gauge.set_value(gpu_mem)
            
            t = len(self.time_history)
            self.time_history.append(t)
            self.cpu_history.append(cpu)
            self.memory_history.append(mem)
            self.gpu_history.append(gpu)
            
            time_data = list(self.time_history)
            self.cpu_curve.setData(time_data, list(self.cpu_history))
            self.memory_curve.setData(time_data, list(self.memory_history))
            self.gpu_curve.setData(time_data, list(self.gpu_history))
            
            freq = self.monitor.cpu_monitor.get_cpu_freq()
            if freq:
                self.freq_card.set_value(f"{freq['current']:.0f} MHz")
            
            mem_info = self.monitor.memory_monitor.get_memory_info()
            self.mem_card.set_value(f"{mem_info['used']:.1f}/{mem_info['total']:.0f} GB")
            
            disk_io = snapshot['disk_io']
            self.disk_read.set_value(f"{disk_io['read_speed']:.1f} MB/s")
            self.disk_write.set_value(f"{disk_io['write_speed']:.1f} MB/s")
            
            net_io = snapshot['network_io']
            self.net_up.set_value(f"{net_io['sent_speed']:.0f} KB/s")
            self.net_down.set_value(f"{net_io['recv_speed']:.0f} KB/s")
            
            if self.is_recording:
                self.record_requested.emit(snapshot)
        
        except Exception as e:
            print(f"更新错误: {e}")
    
    def start_monitoring(self):
        if not self.update_timer.isActive():
            self.update_timer.start()
    
    def stop_monitoring(self):
        self.update_timer.stop()
