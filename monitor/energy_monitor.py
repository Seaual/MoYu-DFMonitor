"""
能耗监控模块 - 估算电脑功耗和碳排放
"""
import psutil
from typing import Dict, Optional
from datetime import datetime, timedelta

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class EnergyMonitor:
    """能耗监控器
    
    基于硬件使用率估算功耗：
    - CPU功耗 ≈ CPU_TDP × (使用率/100) × 负载系数
    - GPU功耗 ≈ GPU_TDP × (使用率/100)
    - 基础功耗（主板、内存、风扇等）
    
    碳排放计算：
    - CO2排放 = 能耗(kWh) × 碳排放因子(kg CO2/kWh)
    - 中国电网平均碳排放因子约 0.5-0.6 kg CO2/kWh
    """
    
    # 默认TDP值（瓦特）- 可根据实际硬件调整
    DEFAULT_CPU_TDP = 65      # 典型桌面CPU TDP
    DEFAULT_GPU_TDP = 150     # 典型独立显卡TDP
    BASE_POWER = 50           # 基础功耗（主板、内存、SSD等）
    
    # 碳排放因子 (kg CO2/kWh) - 中国电网平均值
    CARBON_FACTOR = 0.55
    
    def __init__(self, cpu_tdp: float = None, gpu_tdp: float = None):
        """初始化能耗监控器
        
        Args:
            cpu_tdp: CPU热设计功耗(W)，None则使用默认值
            gpu_tdp: GPU热设计功耗(W)，None则使用默认值
        """
        self.cpu_tdp = cpu_tdp or self.DEFAULT_CPU_TDP
        self.gpu_tdp = gpu_tdp or self.DEFAULT_GPU_TDP
        
        # 检测是否有独立GPU
        self.has_gpu = self._detect_gpu()
        
        # 能耗累计
        self._total_energy_wh = 0.0  # 累计能耗 (Wh)
        self._last_update = datetime.now()
        self._today = datetime.now().date()
        
        # 历史记录
        self._power_history = []  # [(timestamp, power_watts)]
    
    def _detect_gpu(self) -> bool:
        """检测是否有独立GPU"""
        if not GPU_AVAILABLE:
            return False
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
    
    def _reset_daily_if_needed(self):
        """如果跨天则重置累计"""
        today = datetime.now().date()
        if today != self._today:
            self._total_energy_wh = 0.0
            self._power_history.clear()
            self._today = today
    
    def estimate_power(self, cpu_percent: float, gpu_percent: float = 0) -> Dict[str, float]:
        """估算当前功耗
        
        Args:
            cpu_percent: CPU使用率 (0-100)
            gpu_percent: GPU使用率 (0-100)
            
        Returns:
            功耗详情字典
        """
        # CPU功耗估算
        # 使用非线性模型：空闲时约30%TDP，满载时100%TDP
        cpu_load_factor = 0.3 + 0.7 * (cpu_percent / 100)
        cpu_power = self.cpu_tdp * cpu_load_factor
        
        # GPU功耗估算
        if self.has_gpu and gpu_percent > 0:
            # GPU空闲时约10%TDP
            gpu_load_factor = 0.1 + 0.9 * (gpu_percent / 100)
            gpu_power = self.gpu_tdp * gpu_load_factor
        else:
            gpu_power = 0
        
        # 总功耗
        total_power = cpu_power + gpu_power + self.BASE_POWER
        
        return {
            'cpu_power': round(cpu_power, 1),      # CPU功耗 (W)
            'gpu_power': round(gpu_power, 1),      # GPU功耗 (W)
            'base_power': self.BASE_POWER,          # 基础功耗 (W)
            'total_power': round(total_power, 1),  # 总功耗 (W)
        }
    
    def update(self, cpu_percent: float, gpu_percent: float = 0) -> Dict:
        """更新能耗统计
        
        应该每秒调用一次
        
        Args:
            cpu_percent: CPU使用率
            gpu_percent: GPU使用率
            
        Returns:
            能耗统计数据
        """
        self._reset_daily_if_needed()
        
        current_time = datetime.now()
        time_delta = (current_time - self._last_update).total_seconds()
        
        # 估算当前功耗
        power = self.estimate_power(cpu_percent, gpu_percent)
        
        # 累计能耗 (Wh = W × h)
        energy_increment = power['total_power'] * (time_delta / 3600)
        self._total_energy_wh += energy_increment
        
        # 记录历史
        self._power_history.append((current_time, power['total_power']))
        # 只保留最近1小时的数据
        cutoff_time = current_time - timedelta(hours=1)
        self._power_history = [(t, p) for t, p in self._power_history if t > cutoff_time]
        
        self._last_update = current_time
        
        # 计算碳排放
        carbon_emission = self._total_energy_wh / 1000 * self.CARBON_FACTOR
        
        return {
            **power,
            'total_energy_wh': round(self._total_energy_wh, 2),      # 今日累计能耗 (Wh)
            'total_energy_kwh': round(self._total_energy_wh / 1000, 4),  # 今日累计能耗 (kWh)
            'carbon_emission_g': round(carbon_emission * 1000, 1),  # 碳排放 (g CO2)
            'carbon_emission_kg': round(carbon_emission, 4),         # 碳排放 (kg CO2)
        }
    
    def get_average_power(self, minutes: int = 5) -> float:
        """获取最近N分钟的平均功耗
        
        Args:
            minutes: 时间范围（分钟）
            
        Returns:
            平均功耗 (W)
        """
        if not self._power_history:
            return 0
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_data = [p for t, p in self._power_history if t > cutoff_time]
        
        if not recent_data:
            return self._power_history[-1][1] if self._power_history else 0
        
        return round(sum(recent_data) / len(recent_data), 1)
    
    def get_daily_stats(self) -> Dict:
        """获取今日统计"""
        self._reset_daily_if_needed()
        
        avg_power = self.get_average_power(60)  # 最近1小时平均
        carbon = self._total_energy_wh / 1000 * self.CARBON_FACTOR
        
        # 估算全天能耗（如果保持当前使用模式）
        hours_passed = (datetime.now() - datetime.combine(self._today, datetime.min.time())).total_seconds() / 3600
        if hours_passed > 0:
            estimated_daily_kwh = (self._total_energy_wh / hours_passed * 24) / 1000
        else:
            estimated_daily_kwh = 0
        
        return {
            'date': self._today.isoformat(),
            'total_energy_wh': round(self._total_energy_wh, 2),
            'total_energy_kwh': round(self._total_energy_wh / 1000, 4),
            'average_power_w': avg_power,
            'carbon_emission_g': round(carbon * 1000, 1),
            'estimated_daily_kwh': round(estimated_daily_kwh, 3),
            'estimated_daily_carbon_kg': round(estimated_daily_kwh * self.CARBON_FACTOR, 3),
        }
    
    def set_hardware_tdp(self, cpu_tdp: float = None, gpu_tdp: float = None):
        """设置硬件TDP值
        
        Args:
            cpu_tdp: CPU TDP (W)
            gpu_tdp: GPU TDP (W)
        """
        if cpu_tdp is not None:
            self.cpu_tdp = cpu_tdp
        if gpu_tdp is not None:
            self.gpu_tdp = gpu_tdp
