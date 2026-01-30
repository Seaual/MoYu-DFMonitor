"""
数字足迹Tab页 - Apple 设计风格
作为首页，需要最精美的设计
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar,
    QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import pyqtgraph as pg
from collections import deque
from datetime import datetime

from monitor.df_indicators import DFIndicators
from monitor.data_volume_monitor import DataVolumeMonitor
from monitor import SystemMonitor
from .widgets import CircularProgress, MetricCard, GlassCard
from .styles import COLORS, CHART_STYLE


class FootprintTab(QWidget):
    """数字足迹Tab - 首页"""
    
    def __init__(self, system_monitor: SystemMonitor = None, parent=None):
        super().__init__(parent)
        
        self.system_monitor = system_monitor or SystemMonitor()
        self.df_indicators = DFIndicators()
        self.data_monitor = DataVolumeMonitor()
        
        # 历史数据
        self.history_length = 60
        self.power_history = deque(maxlen=self.history_length)
        self.flops_history = deque(maxlen=self.history_length)
        self.time_history = deque(maxlen=self.history_length)
        
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        """设置界面"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(28)
        
        # ============ 顶部欢迎区域 ============
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 132, 255, 0.12),
                    stop:0.5 rgba(94, 92, 230, 0.10),
                    stop:1 rgba(191, 90, 242, 0.12));
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
        """)
        welcome_layout = QHBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(36, 32, 36, 32)
        
        # 左侧文字
        welcome_text = QVBoxLayout()
        welcome_text.setSpacing(10)
        
        greeting = QLabel("👋 你好，欢迎回来")
        greeting.setStyleSheet("""
            color: rgba(255, 255, 255, 0.65);
            font-size: 15px;
            font-weight: 500;
        """)
        welcome_text.addWidget(greeting)
        
        today_label = QLabel(datetime.now().strftime("%Y年%m月%d日"))
        today_label.setStyleSheet("""
            color: #ffffff;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)
        welcome_text.addWidget(today_label)
        
        desc = QLabel("📊 以下是你今天的数字足迹摘要")
        desc.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 14px;")
        welcome_text.addWidget(desc)
        
        welcome_layout.addLayout(welcome_text)
        welcome_layout.addStretch()
        
        # 右侧大数字
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(50)
        
        # 能耗
        energy_box = QVBoxLayout()
        energy_box.setSpacing(6)
        
        energy_icon = QLabel("⚡")
        energy_icon.setStyleSheet("font-size: 24px;")
        energy_box.addWidget(energy_icon, alignment=Qt.AlignRight)
        
        self.hero_energy = QLabel("0")
        self.hero_energy.setStyleSheet("""
            color: #30d158;
            font-size: 42px;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        energy_box.addWidget(self.hero_energy, alignment=Qt.AlignRight)
        energy_unit = QLabel("Wh 能耗")
        energy_unit.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 13px; font-weight: 500;")
        energy_box.addWidget(energy_unit, alignment=Qt.AlignRight)
        summary_layout.addLayout(energy_box)
        
        # 碳排放
        carbon_box = QVBoxLayout()
        carbon_box.setSpacing(6)
        
        carbon_icon = QLabel("🌿")
        carbon_icon.setStyleSheet("font-size: 24px;")
        carbon_box.addWidget(carbon_icon, alignment=Qt.AlignRight)
        
        self.hero_carbon = QLabel("0")
        self.hero_carbon.setStyleSheet("""
            color: #64d2ff;
            font-size: 42px;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        carbon_box.addWidget(self.hero_carbon, alignment=Qt.AlignRight)
        carbon_unit = QLabel("g CO₂")
        carbon_unit.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 13px; font-weight: 500;")
        carbon_box.addWidget(carbon_unit, alignment=Qt.AlignRight)
        summary_layout.addLayout(carbon_box)
        
        welcome_layout.addLayout(summary_layout)
        
        layout.addWidget(welcome_frame)
        
        # ============ 实时性能指标 ============
        section_title = QLabel("⚙️ 实时性能")
        section_title.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding-left: 4px;
        """)
        layout.addWidget(section_title)
        
        realtime_layout = QHBoxLayout()
        realtime_layout.setSpacing(18)
        
        # 四个主要指标
        self.flops_card = MetricCard("计算性能", "🔥", "#ff9f0a")
        realtime_layout.addWidget(self.flops_card)
        
        self.mips_card = MetricCard("指令执行", "⚡", "#30d158")
        realtime_layout.addWidget(self.mips_card)
        
        self.power_card = MetricCard("实时功耗", "🔌", "#ff453a")
        realtime_layout.addWidget(self.power_card)
        
        self.data_card = MetricCard("数据生成", "💾", "#bf5af2")
        realtime_layout.addWidget(self.data_card)
        
        layout.addLayout(realtime_layout)
        
        # ============ DF-LCA 指标 ============
        df_title = QLabel("📐 单位数据指标 (Per-Unit-Data)")
        df_title.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding-left: 4px;
        """)
        layout.addWidget(df_title)
        
        df_layout = QHBoxLayout()
        df_layout.setSpacing(18)
        
        self.tpd_card = MetricCard("TPD", "⏱️", "#0a84ff")
        df_layout.addWidget(self.tpd_card)
        
        self.mpd_card = MetricCard("MPD", "📊", "#5e5ce6")
        df_layout.addWidget(self.mpd_card)
        
        self.wpd_card = MetricCard("WPD", "⚡", "#ff9f0a")
        df_layout.addWidget(self.wpd_card)
        
        self.cpd_card = MetricCard("CPD", "🌱", "#30d158")
        df_layout.addWidget(self.cpd_card)
        
        self.er_card = MetricCard("Effort", "📈", "#bf5af2")
        df_layout.addWidget(self.er_card)
        
        layout.addLayout(df_layout)
        
        # ============ 图表和磁盘区域 ============
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(18)
        
        # 趋势图
        chart_frame = QFrame()
        chart_frame.setObjectName("card")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(24, 22, 24, 22)
        chart_layout.setSpacing(16)
        
        chart_header = QHBoxLayout()
        chart_title = QLabel("📉 性能趋势")
        chart_title.setStyleSheet("""
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
        """)
        chart_header.addWidget(chart_title)
        chart_header.addStretch()
        
        # 图例
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(20)
        
        power_legend = QLabel("🔴 功耗")
        power_legend.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend_layout.addWidget(power_legend)
        
        flops_legend = QLabel("🔵 GFLOPS")
        flops_legend.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        legend_layout.addWidget(flops_legend)
        
        chart_header.addLayout(legend_layout)
        chart_layout.addLayout(chart_header)
        
        self.trend_chart = pg.PlotWidget()
        self._style_chart(self.trend_chart)
        self.trend_chart.setMinimumHeight(220)
        chart_layout.addWidget(self.trend_chart)
        
        charts_layout.addWidget(chart_frame, stretch=2)
        
        # 磁盘使用
        disk_frame = QFrame()
        disk_frame.setObjectName("card")
        disk_layout = QVBoxLayout(disk_frame)
        disk_layout.setContentsMargins(24, 22, 24, 22)
        disk_layout.setSpacing(14)
        
        disk_title = QLabel("💿 存储空间")
        disk_title.setStyleSheet("""
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
        """)
        disk_layout.addWidget(disk_title)
        
        self.disk_label = QLabel("已使用 - / -")
        self.disk_label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px;")
        disk_layout.addWidget(self.disk_label)
        
        self.disk_progress = QProgressBar()
        self.disk_progress.setTextVisible(False)
        self.disk_progress.setFixedHeight(10)
        disk_layout.addWidget(self.disk_progress)
        
        disk_layout.addSpacing(12)
        
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(3)
        self.disk_table.setHorizontalHeaderLabels(['分区', '已用', '使用率'])
        self.disk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.disk_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.disk_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.disk_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.disk_table.verticalHeader().setVisible(False)
        self.disk_table.setShowGrid(False)
        disk_layout.addWidget(self.disk_table)
        
        charts_layout.addWidget(disk_frame, stretch=1)
        
        layout.addLayout(charts_layout)
        
        # ============ 底部公式说明 ============
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 16, 24, 16)
        
        formula = QLabel(
            "<span style='color: rgba(255,255,255,0.5);'>📝 DF-LCA 公式  </span>"
            "<span style='color: #0a84ff;'>TPD</span><span style='color: rgba(255,255,255,0.4);'> = Time÷Data  </span>"
            "<span style='color: #5e5ce6;'>MPD</span><span style='color: rgba(255,255,255,0.4);'> = Instructions÷Data  </span>"
            "<span style='color: #ff9f0a;'>WPD</span><span style='color: rgba(255,255,255,0.4);'> = Energy÷Data  </span>"
            "<span style='color: #30d158;'>CPD</span><span style='color: rgba(255,255,255,0.4);'> = Carbon÷Data  </span>"
            "<span style='color: #bf5af2;'>ER</span><span style='color: rgba(255,255,255,0.4);'> = α·TPD + β·WPD + γ·MPD</span>"
        )
        formula.setStyleSheet("font-size: 12px;")
        footer_layout.addWidget(formula)
        
        layout.addWidget(footer)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _style_chart(self, chart):
        """设置图表样式"""
        chart.setBackground('#1c1c1e')
        chart.getPlotItem().hideAxis('bottom')
        chart.getPlotItem().hideAxis('left')
        chart.setMouseEnabled(x=False, y=False)
        chart.hideButtons()
        
        # 初始化曲线
        self.power_curve = chart.plot(
            pen=pg.mkPen(color='#ff453a', width=2),
            fillLevel=0,
            fillBrush=pg.mkBrush(color=(255, 69, 58, 30))
        )
        self.flops_curve = chart.plot(
            pen=pg.mkPen(color='#0a84ff', width=2)
        )
    
    def _setup_timer(self):
        """设置定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(1000)
        
        self.disk_timer = QTimer()
        self.disk_timer.timeout.connect(self._refresh_disk)
        self.disk_timer.start(30000)
        
        self._refresh_disk()
    
    def _update_data(self):
        """更新数据"""
        try:
            snapshot = self.system_monitor.get_snapshot()
            cpu = snapshot['cpu_percent']
            gpu = snapshot['gpu_percent']
            
            indicators = self.df_indicators.update(cpu, gpu)
            
            # 更新顶部大数字
            energy = indicators['energy_wh']
            if energy < 10:
                self.hero_energy.setText(f"{energy:.2f}")
            elif energy < 100:
                self.hero_energy.setText(f"{energy:.1f}")
            else:
                self.hero_energy.setText(f"{energy:.0f}")
            
            carbon = indicators['carbon_g']
            if carbon < 10:
                self.hero_carbon.setText(f"{carbon:.2f}")
            elif carbon < 100:
                self.hero_carbon.setText(f"{carbon:.1f}")
            else:
                self.hero_carbon.setText(f"{carbon:.0f}")
            
            # 实时指标
            self.flops_card.set_value(
                f"{indicators['flops']['total_gflops']:.1f}",
                "GFLOPS"
            )
            self.mips_card.set_value(
                f"{indicators['mips']['mips']:.0f}",
                "MIPS"
            )
            self.power_card.set_value(
                f"{indicators['power']['total_power_w']:.0f}",
                "W"
            )
            
            data_stats = self.data_monitor.update()
            self.data_card.set_value(
                f"{data_stats['total_generated_mb']:.1f}",
                "MB 今日"
            )
            
            # DF-LCA 指标
            self.tpd_card.set_value(f"{indicators['tpd']:.3f}", "s/MB")
            self.mpd_card.set_value(f"{indicators['mpd']:.1f}", "MI/MB")
            self.wpd_card.set_value(f"{indicators['wpd']*1000:.2f}", "mWh/MB")
            self.cpd_card.set_value(f"{indicators['cpd']:.3f}", "gCO₂/MB")
            self.er_card.set_value(f"{indicators['effort_rate']:.3f}", "综合成本")
            
            # 更新图表
            t = len(self.time_history)
            self.time_history.append(t)
            self.power_history.append(indicators['power']['total_power_w'])
            self.flops_history.append(indicators['flops']['total_gflops'])
            
            self.power_curve.setData(list(self.time_history), list(self.power_history))
            self.flops_curve.setData(list(self.time_history), list(self.flops_history))
        
        except Exception as e:
            print(f"更新错误: {e}")
    
    def _refresh_disk(self):
        """刷新磁盘"""
        try:
            disk = self.data_monitor.get_total_disk_usage()
            
            self.disk_label.setText(
                f"已使用 {disk['used_gb']:.0f} GB / {disk['total_gb']:.0f} GB"
            )
            self.disk_progress.setValue(int(disk['percent']))
            
            partitions = disk['partitions']
            self.disk_table.setRowCount(len(partitions))
            
            for i, p in enumerate(partitions):
                self.disk_table.setItem(i, 0, QTableWidgetItem(p['mountpoint']))
                self.disk_table.setItem(i, 1, QTableWidgetItem(f"{p['used_gb']:.0f} GB"))
                
                percent_item = QTableWidgetItem(f"{p['percent']:.0f}%")
                if p['percent'] >= 90:
                    percent_item.setForeground(QColor("#ff453a"))
                elif p['percent'] >= 70:
                    percent_item.setForeground(QColor("#ff9f0a"))
                else:
                    percent_item.setForeground(QColor("#30d158"))
                self.disk_table.setItem(i, 2, percent_item)
        
        except Exception as e:
            print(f"磁盘刷新错误: {e}")
    
    def start_monitoring(self):
        if not self.update_timer.isActive():
            self.update_timer.start()
    
    def stop_monitoring(self):
        self.update_timer.stop()
        self.disk_timer.stop()
