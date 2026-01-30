"""
CPU监控模块
"""
import psutil
from typing import Dict, List, Optional


class CPUMonitor:
    """CPU监控类"""
    
    def __init__(self):
        # 初始化时获取一次CPU信息，避免第一次调用返回0
        psutil.cpu_percent(interval=None)
    
    def get_cpu_percent(self) -> float:
        """获取CPU总体利用率"""
        return psutil.cpu_percent(interval=None)
    
    def get_cpu_percent_per_core(self) -> List[float]:
        """获取每个CPU核心的利用率"""
        return psutil.cpu_percent(interval=None, percpu=True)
    
    def get_cpu_freq(self) -> Optional[Dict[str, float]]:
        """获取CPU频率信息"""
        freq = psutil.cpu_freq()
        if freq:
            return {
                'current': freq.current,  # 当前频率 MHz
                'min': freq.min,          # 最小频率 MHz
                'max': freq.max           # 最大频率 MHz
            }
        return None
    
    def get_cpu_count(self) -> Dict[str, int]:
        """获取CPU核心数"""
        return {
            'physical': psutil.cpu_count(logical=False),  # 物理核心数
            'logical': psutil.cpu_count(logical=True)     # 逻辑核心数
        }
    
    def get_cpu_stats(self) -> Dict[str, int]:
        """获取CPU统计信息"""
        stats = psutil.cpu_stats()
        return {
            'ctx_switches': stats.ctx_switches,    # 上下文切换次数
            'interrupts': stats.interrupts,        # 中断次数
            'soft_interrupts': stats.soft_interrupts,  # 软中断次数
            'syscalls': stats.syscalls             # 系统调用次数
        }
    
    def get_all_info(self) -> Dict:
        """获取所有CPU信息"""
        return {
            'percent': self.get_cpu_percent(),
            'percent_per_core': self.get_cpu_percent_per_core(),
            'frequency': self.get_cpu_freq(),
            'count': self.get_cpu_count(),
            'stats': self.get_cpu_stats()
        }
