"""
数据量监控模块 - 统计数据生成量（DF Performance维度）
"""
import psutil
from typing import Dict, List
from datetime import datetime
from pathlib import Path


class DataVolumeMonitor:
    """数据量监控器
    
    监控数字足迹中的数据量指标：
    - 磁盘写入量（数据生成）
    - 网络上传量（数据传输）
    - 磁盘空间使用情况
    """
    
    def __init__(self):
        # 初始化基准值
        self._init_counters()
        
        # 今日统计
        self._today = datetime.now().date()
        self._daily_disk_write = 0  # 今日磁盘写入 (bytes)
        self._daily_net_upload = 0  # 今日网络上传 (bytes)
        self._daily_disk_read = 0   # 今日磁盘读取 (bytes)
        self._daily_net_download = 0  # 今日网络下载 (bytes)
    
    def _init_counters(self):
        """初始化计数器基准值"""
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        self._last_disk_write = disk_io.write_bytes if disk_io else 0
        self._last_disk_read = disk_io.read_bytes if disk_io else 0
        self._last_net_sent = net_io.bytes_sent if net_io else 0
        self._last_net_recv = net_io.bytes_recv if net_io else 0
        self._last_update = datetime.now()
    
    def _reset_daily_if_needed(self):
        """如果跨天则重置统计"""
        today = datetime.now().date()
        if today != self._today:
            self._daily_disk_write = 0
            self._daily_net_upload = 0
            self._daily_disk_read = 0
            self._daily_net_download = 0
            self._today = today
            self._init_counters()
    
    def update(self) -> Dict:
        """更新数据量统计
        
        Returns:
            数据量统计信息
        """
        self._reset_daily_if_needed()
        
        current_time = datetime.now()
        
        # 获取当前计数器
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        if disk_io:
            # 计算增量
            disk_write_delta = disk_io.write_bytes - self._last_disk_write
            disk_read_delta = disk_io.read_bytes - self._last_disk_read
            
            # 处理计数器溢出或重置
            if disk_write_delta < 0:
                disk_write_delta = disk_io.write_bytes
            if disk_read_delta < 0:
                disk_read_delta = disk_io.read_bytes
            
            # 累计今日数据
            self._daily_disk_write += disk_write_delta
            self._daily_disk_read += disk_read_delta
            
            # 更新基准
            self._last_disk_write = disk_io.write_bytes
            self._last_disk_read = disk_io.read_bytes
        
        if net_io:
            # 计算增量
            net_sent_delta = net_io.bytes_sent - self._last_net_sent
            net_recv_delta = net_io.bytes_recv - self._last_net_recv
            
            # 处理计数器溢出
            if net_sent_delta < 0:
                net_sent_delta = net_io.bytes_sent
            if net_recv_delta < 0:
                net_recv_delta = net_io.bytes_recv
            
            # 累计
            self._daily_net_upload += net_sent_delta
            self._daily_net_download += net_recv_delta
            
            # 更新基准
            self._last_net_sent = net_io.bytes_sent
            self._last_net_recv = net_io.bytes_recv
        
        self._last_update = current_time
        
        # 计算总数据生成量 = 磁盘写入 + 网络上传
        total_data_generated = self._daily_disk_write + self._daily_net_upload
        
        # 计算总数据消费量 = 磁盘读取 + 网络下载
        total_data_consumed = self._daily_disk_read + self._daily_net_download
        
        return {
            # 今日数据生成
            'disk_write_bytes': self._daily_disk_write,
            'disk_write_mb': round(self._daily_disk_write / (1024**2), 2),
            'disk_write_gb': round(self._daily_disk_write / (1024**3), 3),
            
            # 今日网络上传
            'net_upload_bytes': self._daily_net_upload,
            'net_upload_mb': round(self._daily_net_upload / (1024**2), 2),
            'net_upload_gb': round(self._daily_net_upload / (1024**3), 3),
            
            # 今日磁盘读取
            'disk_read_bytes': self._daily_disk_read,
            'disk_read_mb': round(self._daily_disk_read / (1024**2), 2),
            'disk_read_gb': round(self._daily_disk_read / (1024**3), 3),
            
            # 今日网络下载
            'net_download_bytes': self._daily_net_download,
            'net_download_mb': round(self._daily_net_download / (1024**2), 2),
            'net_download_gb': round(self._daily_net_download / (1024**3), 3),
            
            # 总数据生成量（数字足迹核心指标）
            'total_generated_bytes': total_data_generated,
            'total_generated_mb': round(total_data_generated / (1024**2), 2),
            'total_generated_gb': round(total_data_generated / (1024**3), 3),
            
            # 总数据消费量
            'total_consumed_bytes': total_data_consumed,
            'total_consumed_mb': round(total_data_consumed / (1024**2), 2),
            'total_consumed_gb': round(total_data_consumed / (1024**3), 3),
        }
    
    def get_disk_usage(self) -> List[Dict]:
        """获取磁盘空间使用情况
        
        Returns:
            各分区使用情况列表
        """
        partitions = psutil.disk_partitions()
        result = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                result.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_bytes': usage.total,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_bytes': usage.used,
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_bytes': usage.free,
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent': usage.percent,
                })
            except (PermissionError, OSError):
                continue
        
        return result
    
    def get_total_disk_usage(self) -> Dict:
        """获取总磁盘使用情况"""
        partitions = self.get_disk_usage()
        
        total = sum(p['total_bytes'] for p in partitions)
        used = sum(p['used_bytes'] for p in partitions)
        free = sum(p['free_bytes'] for p in partitions)
        
        return {
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'percent': round(used / total * 100, 1) if total > 0 else 0,
            'partitions': partitions,
        }
    
    def get_daily_summary(self) -> Dict:
        """获取今日数据量摘要"""
        self._reset_daily_if_needed()
        
        data = self.update()
        disk = self.get_total_disk_usage()
        
        return {
            'date': self._today.isoformat(),
            
            # 数据生成（DF Performance核心指标）
            'data_generated_gb': data['total_generated_gb'],
            'disk_write_gb': data['disk_write_gb'],
            'net_upload_gb': data['net_upload_gb'],
            
            # 数据消费
            'data_consumed_gb': data['total_consumed_gb'],
            'disk_read_gb': data['disk_read_gb'],
            'net_download_gb': data['net_download_gb'],
            
            # 磁盘空间
            'disk_total_gb': disk['total_gb'],
            'disk_used_gb': disk['used_gb'],
            'disk_free_gb': disk['free_gb'],
            'disk_percent': disk['percent'],
        }
    
    @staticmethod
    def format_bytes(bytes_val: int) -> str:
        """格式化字节数显示"""
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024**2:
            return f"{bytes_val/1024:.1f} KB"
        elif bytes_val < 1024**3:
            return f"{bytes_val/(1024**2):.2f} MB"
        else:
            return f"{bytes_val/(1024**3):.2f} GB"
