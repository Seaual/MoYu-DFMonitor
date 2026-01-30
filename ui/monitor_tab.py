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
        
        self.cpu_gauge = CircularProgress("🖥️ CPU", 120)
        self.cpu_gauge.set_colors("#0a84ff", "#5e5ce6")
        gauges_layout.addWidget(self.cpu_gauge, alignment=Qt.AlignCenter)
        
        self.memory_gauge = CircularProgress("💾 内存", 120)
        self.memory_gauge.set_colors("#30d158", "#64d2ff")
        gauges_layout.addWidget(self.memory_gauge, alignment=Qt.AlignCenter)
        
        self.gpu_gauge = CircularProgress("🎮 GPU", 120)
        self.gpu_gauge.set_colors("#bf5af2", "#ff375f")
        gauges_layout.addWidget(self.gpu_gauge, alignment=Qt.AlignCenter)
        
        self.gpu_mem_gauge = CircularProgress("📦 显存", 120)
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
        chart_title = QLabel("📈 使用率趋势")
        chart_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        chart_header.addWidget(chart_title)
        chart_header.addStretch()
        
        legend = QHBoxLayout()
        legend.setSpacing(18)
        legend.addWidget(QLabel("🔵 CPU"), alignment=Qt.AlignRight)
        legend.itemAt(0).widget().setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend.addWidget(QLabel("🟢 内存"))
        legend.itemAt(1).widget().setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend.addWidget(QLabel("🟣 GPU"))
        legend.itemAt(2).widget().setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        chart_header.addLayout(legend)
        
        chart_layout.addLayout(chart_header)
        
        self.plot_widget = pg.PlotWidget()
        self._style_chart(self.plot_widget)
        chart_layout.addWidget(self.plot_widget)
        
        middle_layout.addWidget(chart_frame, stretch=3)
        
        # 统计卡片
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(14)
        
        self.freq_card = StatCard("CPU 频率", "-", "⚡")
        stats_layout.addWidget(self.freq_card)
        
        self.mem_card = StatCard("内存使用", "-", "💾")
        stats_layout.addWidget(self.mem_card)
        
        self.disk_read = StatCard("磁盘读取", "-", "📖")
        stats_layout.addWidget(self.disk_read)
        
        self.disk_write = StatCard("磁盘写入", "-", "✏️")
        stats_layout.addWidget(self.disk_write)
        
        self.net_up = StatCard("网络上传", "-", "📤")
        stats_layout.addWidget(self.net_up)
        
        self.net_down = StatCard("网络下载", "-", "📥")
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
            self.gpu_status.setText("✅ GPU 已连接")
            self.gpu_status.setStyleSheet("color: #30d158; font-size: 13px; font-weight: 500;")
        else:
            self.gpu_status.setText("⚪ GPU 未检测到")
            self.gpu_status.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 13px;")
        control_layout.addWidget(self.gpu_status)
        
        control_layout.addStretch()
        
        interval_label = QLabel("⏱️ 采样间隔")
        interval_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 13px;")
        control_layout.addWidget(interval_label)
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['1 秒', '2 秒', '5 秒'])
        self.interval_combo.setFixedWidth(90)
        self.interval_combo.currentIndexChanged.connect(self._on_interval_changed)
        control_layout.addWidget(self.interval_combo)
        
        control_layout.addSpacing(20)
        
        self.record_btn = QPushButton("🔴 开始记录")
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
            self.record_btn.setText("⏹️ 停止记录")
            self.record_btn.setStyleSheet("background-color: #ff453a;")
        else:
            self.record_btn.setText("🔴 开始记录")
            self.record_btn.setStyleSheet("")
    
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
