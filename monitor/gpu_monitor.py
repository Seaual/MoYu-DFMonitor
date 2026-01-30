"""
GPU监控模块 (支持NVIDIA GPU)
"""
from typing import Dict, List, Optional

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class GPUMonitor:
    """GPU监控类"""
    
    def __init__(self):
        self.available = GPU_AVAILABLE
    
    def is_available(self) -> bool:
        """检查GPU监控是否可用"""
        if not self.available:
            return False
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except Exception:
            return False
    
    def get_gpu_info(self) -> Optional[List[Dict]]:
        """获取所有GPU信息"""
        if not self.available:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None
            
            result = []
            for gpu in gpus:
                result.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,              # GPU利用率 %
                    'memory_total': gpu.memoryTotal,     # 显存总量 MB
                    'memory_used': gpu.memoryUsed,       # 已用显存 MB
                    'memory_free': gpu.memoryFree,       # 空闲显存 MB
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) 
                                      if gpu.memoryTotal > 0 else 0,
                    'temperature': gpu.temperature,      # 温度 °C
                    'driver': gpu.driver                 # 驱动版本
                })
            return result
        except Exception:
            return None
    
    def get_gpu_percent(self) -> float:
        """获取第一个GPU的利用率"""
        info = self.get_gpu_info()
        if info and len(info) > 0:
            return info[0]['load']
        return 0.0
    
    def get_gpu_memory_percent(self) -> float:
        """获取第一个GPU的显存使用率"""
        info = self.get_gpu_info()
        if info and len(info) > 0:
            return info[0]['memory_percent']
        return 0.0
    
    def get_gpu_temperature(self) -> float:
        """获取第一个GPU的温度"""
        info = self.get_gpu_info()
        if info and len(info) > 0:
            return info[0]['temperature']
        return 0.0
    
    def get_all_info(self) -> Dict:
        """获取所有GPU信息"""
        return {
            'available': self.is_available(),
            'gpus': self.get_gpu_info()
        }
