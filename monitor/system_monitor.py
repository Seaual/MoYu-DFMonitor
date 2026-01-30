"""
系统监控综合模块
"""
import psutil
from typing import Dict
from datetime import datetime

from .cpu_monitor import CPUMonitor
from .memory_monitor import MemoryMonitor
from .gpu_monitor import GPUMonitor


class SystemMonitor:
    """系统监控综合类"""
    
    def __init__(self):
        self.cpu_monitor = CPUMonitor()
        self.memory_monitor = MemoryMonitor()
        self.gpu_monitor = GPUMonitor()
        
        # 用于计算网络和磁盘速度
        self._last_net_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()
        self._last_time = datetime.now()
    
    def get_disk_io(self) -> Dict[str, float]:
        """获取磁盘IO信息"""
        current_io = psutil.disk_io_counters()
        current_time = datetime.now()
        
        time_delta = (current_time - self._last_time).total_seconds()
        if time_delta <= 0:
            time_delta = 1
        
        # 计算读写速度 (MB/s)
        read_speed = (current_io.read_bytes - self._last_disk_io.read_bytes) / time_delta / (1024 ** 2)
        write_speed = (current_io.write_bytes - self._last_disk_io.write_bytes) / time_delta / (1024 ** 2)
        
        self._last_disk_io = current_io
        
        return {
            'read_speed': max(0, read_speed),   # 读取速度 MB/s
            'write_speed': max(0, write_speed), # 写入速度 MB/s
            'read_count': current_io.read_count,
            'write_count': current_io.write_count
        }
    
    def get_network_io(self) -> Dict[str, float]:
        """获取网络IO信息"""
        current_io = psutil.net_io_counters()
        current_time = datetime.now()
        
        time_delta = (current_time - self._last_time).total_seconds()
        if time_delta <= 0:
            time_delta = 1
        
        # 计算上传下载速度 (KB/s)
        sent_speed = (current_io.bytes_sent - self._last_net_io.bytes_sent) / time_delta / 1024
        recv_speed = (current_io.bytes_recv - self._last_net_io.bytes_recv) / time_delta / 1024
        
        self._last_net_io = current_io
        self._last_time = current_time
        
        return {
            'sent_speed': max(0, sent_speed),    # 上传速度 KB/s
            'recv_speed': max(0, recv_speed),    # 下载速度 KB/s
            'bytes_sent': current_io.bytes_sent / (1024 ** 2),  # 总发送 MB
            'bytes_recv': current_io.bytes_recv / (1024 ** 2)   # 总接收 MB
        }
    
    def get_disk_usage(self) -> Dict[str, Dict]:
        """获取磁盘使用情况"""
        partitions = psutil.disk_partitions()
        usage = {}
        
        for partition in partitions:
            try:
                part_usage = psutil.disk_usage(partition.mountpoint)
                usage[partition.mountpoint] = {
                    'total': part_usage.total / (1024 ** 3),      # GB
                    'used': part_usage.used / (1024 ** 3),        # GB
                    'free': part_usage.free / (1024 ** 3),        # GB
                    'percent': part_usage.percent
                }
            except Exception:
                continue
        
        return usage
    
    def get_snapshot(self) -> Dict:
        """获取系统状态快照（用于定时采集）"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': self.cpu_monitor.get_cpu_percent(),
            'memory_percent': self.memory_monitor.get_memory_percent(),
            'gpu_percent': self.gpu_monitor.get_gpu_percent(),
            'gpu_memory_percent': self.gpu_monitor.get_gpu_memory_percent(),
            'disk_io': self.get_disk_io(),
            'network_io': self.get_network_io()
        }
    
    def get_all_info(self) -> Dict:
        """获取所有系统信息"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.cpu_monitor.get_all_info(),
            'memory': self.memory_monitor.get_all_info(),
            'gpu': self.gpu_monitor.get_all_info(),
            'disk_io': self.get_disk_io(),
            'network_io': self.get_network_io(),
            'disk_usage': self.get_disk_usage()
        }
