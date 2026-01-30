"""
自定义组件 - Apple 设计风格
简洁、优雅、动效流畅
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGraphicsDropShadowEffect, QSizePolicy,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    pyqtProperty, QPoint, QParallelAnimationGroup,
    QSequentialAnimationGroup, QRect
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont, QLinearGradient, 
    QPainterPath, QBrush, QRadialGradient
)

import math


class GlassCard(QFrame):
    """玻璃形态卡片 - Apple Liquid Glass 风格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        # 添加柔和阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


class CircularProgress(QWidget):
    """圆形进度条 - Apple Watch 风格"""
    
    def __init__(self, title: str = "", size: int = 120, parent=None):
        super().__init__(parent)
        self.title = title
        self._value = 0
        self._animated_value = 0
        self._size = size
        
        self.setFixedSize(size + 40, size + 56)
        
        # 平滑动画
        self._animation = QPropertyAnimation(self, b"animated_value")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 默认渐变色
        self.gradient_start = QColor("#0a84ff")
        self.gradient_end = QColor("#bf5af2")
    
    def get_animated_value(self):
        return self._animated_value
    
    def set_animated_value(self, value):
        self._animated_value = value
        self.update()
    
    animated_value = pyqtProperty(float, get_animated_value, set_animated_value)
    
    def set_value(self, value: float):
        """设置进度值并触发动画"""
        self._value = max(0, min(100, value))
        self._animation.setStartValue(self._animated_value)
        self._animation.setEndValue(self._value)
        self._animation.start()
        
        # 根据值动态调整颜色
        if value >= 90:
            self.gradient_start = QColor("#ff453a")
            self.gradient_end = QColor("#ff9f0a")
        elif value >= 70:
            self.gradient_start = QColor("#ff9f0a")
            self.gradient_end = QColor("#ffd60a")
        else:
            self.gradient_start = QColor("#0a84ff")
            self.gradient_end = QColor("#bf5af2")
    
    def set_colors(self, start: str, end: str):
        """设置渐变颜色"""
        self.gradient_start = QColor(start)
        self.gradient_end = QColor(end)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = (self.height() - 40) // 2
        radius = self._size // 2 - 10
        
        # 绘制背景轨道
        pen = QPen(QColor(255, 255, 255, 20), 10)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2,
            0, 360 * 16
        )
        
        # 绘制进度圆弧
        if self._animated_value > 0:
            gradient = QLinearGradient(
                center_x - radius, center_y,
                center_x + radius, center_y
            )
            gradient.setColorAt(0, self.gradient_start)
            gradient.setColorAt(1, self.gradient_end)
            
            pen = QPen()
            pen.setBrush(QBrush(gradient))
            pen.setWidth(10)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            span = int(-self._animated_value * 360 / 100 * 16)
            painter.drawArc(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2,
                90 * 16, span
            )
        
        # 绘制中心数值
        painter.setPen(QColor("#ffffff"))
        font = QFont("SF Pro Display", 32, QFont.Bold)
        painter.setFont(font)
        painter.drawText(
            0, center_y - 24, self.width(), 48,
            Qt.AlignCenter, f"{int(self._animated_value)}"
        )
        
        # 绘制百分号
        painter.setPen(QColor(255, 255, 255, 100))
        font = QFont("SF Pro Display", 13)
        painter.setFont(font)
        painter.drawText(
            0, center_y + 16, self.width(), 24,
            Qt.AlignCenter, "%"
        )
        
        # 绘制标题
        painter.setPen(QColor(255, 255, 255, 140))
        font = QFont("SF Pro Display", 13, QFont.Medium)
        painter.setFont(font)
        painter.drawText(
            0, self.height() - 28, self.width(), 24,
            Qt.AlignCenter, self.title
        )


class MetricCard(QFrame):
    """指标卡片 - 现代简约风格"""
    
    def __init__(self, title: str, icon: str = "", 
                 accent_color: str = "#0a84ff", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.accent_color = accent_color
        
        self.setMinimumHeight(120)
        self.setMinimumWidth(180)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        
        # 标题行
        header = QHBoxLayout()
        header.setSpacing(10)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: 22px;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title.upper())
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.55);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.2px;
        """)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # 数值
        self.value_label = QLabel("-")
        self.value_label.setStyleSheet(f"""
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
            font-family: "SF Pro Display", "Segoe UI", sans-serif;
        """)
        layout.addWidget(self.value_label)
        
        # 单位/描述
        self.subtitle_label = QLabel("")
        self.subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.45);
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
    
    def set_value(self, value: str, subtitle: str = ""):
        self.value_label.setText(value)
        if subtitle:
            self.subtitle_label.setText(subtitle)
    
    def set_accent_value(self, value: str, subtitle: str = ""):
        """使用强调色显示数值"""
        self.value_label.setStyleSheet(f"""
            color: {self.accent_color};
            font-size: 24px;
            font-weight: 700;
            font-family: "SF Pro Display", "Segoe UI", sans-serif;
        """)
        self.set_value(value, subtitle)


class StatCard(QFrame):
    """统计卡片 - 简洁版"""
    
    def __init__(self, title: str, value: str = "-", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(170, 90)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 35))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        
        # 标题
        header = QHBoxLayout()
        header.setSpacing(8)
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 12px; font-weight: 500;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # 数值
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: #ffffff;
            font-size: 22px;
            font-weight: 600;
        """)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
    
    def set_value(self, value: str):
        self.value_label.setText(value)
    
    def set_color(self, color: str):
        self.value_label.setStyleSheet(f"""
            color: {color};
            font-size: 22px;
            font-weight: 600;
        """)


class MiniChart(QWidget):
    """迷你图表 - 面积图风格"""
    
    def __init__(self, color: str = "#0a84ff", parent=None):
        super().__init__(parent)
        self.data = []
        self.color = QColor(color)
        self.setMinimumSize(100, 40)
    
    def set_data(self, data: list):
        self.data = data[-30:]
        self.update()
    
    def set_color(self, color: str):
        self.color = QColor(color)
        self.update()
    
    def paintEvent(self, event):
        if len(self.data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        margin = 2
        
        max_val = max(self.data) if max(self.data) > 0 else 1
        min_val = min(self.data)
        val_range = max_val - min_val if max_val > min_val else 1
        
        # 计算点
        points = []
        for i, val in enumerate(self.data):
            x = margin + (w - 2 * margin) * i / (len(self.data) - 1)
            y = h - margin - (h - 2 * margin) * (val - min_val) / val_range
            points.append((x, y))
        
        # 绘制填充区域
        fill_path = QPainterPath()
        fill_path.moveTo(points[0][0], h)
        for x, y in points:
            fill_path.lineTo(x, y)
        fill_path.lineTo(points[-1][0], h)
        fill_path.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, h)
        fill_color = QColor(self.color)
        fill_color.setAlpha(60)
        gradient.setColorAt(0, fill_color)
        fill_color.setAlpha(0)
        gradient.setColorAt(1, fill_color)
        painter.fillPath(fill_path, gradient)
        
        # 绘制线条
        line_path = QPainterPath()
        line_path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            line_path.lineTo(x, y)
        
        pen = QPen(self.color, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(line_path)


class GlowButton(QFrame):
    """发光按钮"""
    
    def __init__(self, text: str, color: str = "#0a84ff", parent=None):
        super().__init__(parent)
        self.text = text
        self.color = color
        self._active = False
        
        self.setMinimumSize(100, 36)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"""
            color: {color};
            font-weight: 600;
            font-size: 13px;
        """)
        layout.addWidget(self.label)
        
        self._update_style()
    
    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color};
                    border-radius: 10px;
                }}
            """)
            self.label.setStyleSheet("color: white; font-weight: 600; font-size: 13px;")
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(255, 255, 255, 0.08);
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    background-color: rgba(255, 255, 255, 0.12);
                }}
            """)
            self.label.setStyleSheet(f"color: {self.color}; font-weight: 600; font-size: 13px;")
    
    def set_active(self, active: bool):
        self._active = active
        self._update_style()
    
    def mousePressEvent(self, event):
        self._active = not self._active
        self._update_style()
        super().mousePressEvent(event)


class AnimatedLabel(QLabel):
    """带动画的数值标签"""
    
    def __init__(self, text: str = "0", parent=None):
        super().__init__(text, parent)
        self._value = 0
        self._target = 0
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.setInterval(16)
    
    def set_value(self, value: float, animated: bool = True):
        self._target = value
        if animated and not self._timer.isActive():
            self._timer.start()
        elif not animated:
            self._value = value
            self.setText(f"{value:.1f}")
    
    def _animate(self):
        diff = self._target - self._value
        if abs(diff) < 0.1:
            self._value = self._target
            self._timer.stop()
        else:
            self._value += diff * 0.15
        self.setText(f"{self._value:.1f}")
