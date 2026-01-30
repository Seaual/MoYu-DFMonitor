"""
内存监控模块
"""
import psutil
from typing import Dict


class MemoryMonitor:
    """内存监控类"""
    
    def get_memory_info(self) -> Dict[str, float]:
        """获取内存使用信息"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total / (1024 ** 3),          # 总内存 GB
            'available': mem.available / (1024 ** 3),  # 可用内存 GB
            'used': mem.used / (1024 ** 3),            # 已用内存 GB
            'percent': mem.percent,                     # 使用率 %
            'free': mem.free / (1024 ** 3)             # 空闲内存 GB
        }
    
    def get_memory_percent(self) -> float:
        """获取内存使用率"""
        return psutil.virtual_memory().percent
    
    def get_swap_info(self) -> Dict[str, float]:
        """获取交换分区信息"""
        swap = psutil.swap_memory()
        return {
            'total': swap.total / (1024 ** 3),    # 总交换空间 GB
            'used': swap.used / (1024 ** 3),      # 已用交换空间 GB
            'free': swap.free / (1024 ** 3),      # 空闲交换空间 GB
            'percent': swap.percent,               # 使用率 %
            'sin': swap.sin / (1024 ** 2),        # 从磁盘换入 MB
            'sout': swap.sout / (1024 ** 2)       # 换出到磁盘 MB
        }
    
    def get_all_info(self) -> Dict:
        """获取所有内存信息"""
        return {
            'memory': self.get_memory_info(),
            'swap': self.get_swap_info()
        }
