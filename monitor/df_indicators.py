"""
数字足迹指标计算模块 (DF-LCA Indicators)

基于论文: "How to assess the digitization and digital effort: 
A framework for Digitization Footprint (Part 1)"

指标体系：
- Performance: FLOPS, MIPS, TPD, MPD, 数据量
- Energy: WPD, CPD, 能耗
- Value: ER, VPD

公式参考论文 Formula (10)-(14)
"""
import psutil
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


@dataclass
class HardwareSpecs:
    """硬件规格配置"""
    # CPU规格
    cpu_cores: int = 8                    # CPU核心数
    cpu_freq_ghz: float = 3.5             # CPU频率 (GHz)
    cpu_ipc: float = 4.0                  # 每周期指令数 (IPC, 现代CPU约2-5)
    cpu_flops_per_cycle: float = 16.0     # 每周期浮点运算数 (AVX2约16)
    cpu_tdp: float = 65.0                 # CPU TDP (W)
    
    # GPU规格 (NVIDIA)
    gpu_cores: int = 2048                 # CUDA核心数
    gpu_freq_ghz: float = 1.5             # GPU频率 (GHz)
    gpu_flops_per_core: float = 2.0       # 每核心每周期FLOPS
    gpu_tdp: float = 150.0                # GPU TDP (W)
    
    # 系统基础功耗
    base_power: float = 50.0              # 基础功耗 (W)


class DFIndicators:
    """数字足迹指标计算器
    
    实现论文中定义的DF-LCA指标体系：
    
    Performance Indicators (UP):
        - FLOPS: 浮点运算能力 (GFLOPS)
        - MIPS: 每秒百万指令数
        - TPD: Time Per unit Data (s/MB)
        - MPD: Million Instructions Per Data (MI/MB)
        - Data Volume: 数据生成量
    
    Energy Indicators (UE):
        - Power: 实时功耗 (W)
        - Energy: 累计能耗 (Wh)
        - WPD: Watt Per unit Data (W/MB)
        - CPD: Carbon Per unit Data (g CO2/MB)
    
    Value Indicators (UV):
        - ER: Effort Rate - 综合成本指标
        - DPU Efficiency: 数据处理效率
    
    根据论文公式(10)-(11):
        UI = UP ∪ UE ∪ UV
        UM = UMP ∪ UME ∪ UMV
    """
    
    # 碳排放因子 (kg CO2/kWh) - 中国电网平均
    CARBON_FACTOR = 0.55
    
    def __init__(self, specs: HardwareSpecs = None):
        """初始化指标计算器
        
        Args:
            specs: 硬件规格配置，None则自动检测
        """
        self.specs = specs or self._auto_detect_specs()
        
        # 计算理论峰值性能
        self._calc_theoretical_peaks()
        
        # 累计统计
        self._today = datetime.now().date()
        self._total_flops = 0.0           # 累计FLOPS
        self._total_instructions = 0.0    # 累计指令数
        self._total_energy_wh = 0.0       # 累计能耗
        self._total_data_bytes = 0.0      # 累计数据量
        self._total_time_s = 0.0          # 累计处理时间
        
        # 用于计算增量
        self._last_disk_write = 0
        self._last_net_upload = 0
        self._last_update = datetime.now()
        
        self._init_counters()
    
    def _auto_detect_specs(self) -> HardwareSpecs:
        """自动检测硬件规格"""
        specs = HardwareSpecs()
        
        # 检测CPU
        specs.cpu_cores = psutil.cpu_count(logical=False) or 4
        freq = psutil.cpu_freq()
        if freq:
            specs.cpu_freq_ghz = freq.max / 1000 if freq.max else 3.0
        
        # 检测GPU
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    # 简单估算CUDA核心数（基于显存大小）
                    mem_gb = gpus[0].memoryTotal / 1024
                    specs.gpu_cores = int(mem_gb * 500)  # 粗略估算
                    specs.gpu_tdp = 150 if mem_gb > 4 else 75
            except:
                pass
        
        return specs
    
    def _calc_theoretical_peaks(self):
        """计算理论峰值性能"""
        # CPU理论峰值FLOPS (GFLOPS)
        # FLOPS = cores × freq × flops_per_cycle
        self.cpu_peak_gflops = (
            self.specs.cpu_cores * 
            self.specs.cpu_freq_ghz * 
            self.specs.cpu_flops_per_cycle
        )
        
        # CPU理论峰值MIPS
        # MIPS = cores × freq × IPC × 1000
        self.cpu_peak_mips = (
            self.specs.cpu_cores * 
            self.specs.cpu_freq_ghz * 
            self.specs.cpu_ipc * 
            1000
        )
        
        # GPU理论峰值FLOPS (GFLOPS)
        self.gpu_peak_gflops = (
            self.specs.gpu_cores * 
            self.specs.gpu_freq_ghz * 
            self.specs.gpu_flops_per_core
        )
        
        # 系统总峰值
        self.total_peak_gflops = self.cpu_peak_gflops + self.gpu_peak_gflops
        self.total_peak_mips = self.cpu_peak_mips
    
    def _init_counters(self):
        """初始化IO计数器"""
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        if disk_io:
            self._last_disk_write = disk_io.write_bytes
        if net_io:
            self._last_net_upload = net_io.bytes_sent
    
    def _reset_daily_if_needed(self):
        """跨天重置"""
        today = datetime.now().date()
        if today != self._today:
            self._total_flops = 0.0
            self._total_instructions = 0.0
            self._total_energy_wh = 0.0
            self._total_data_bytes = 0.0
            self._total_time_s = 0.0
            self._today = today
            self._init_counters()
    
    def calculate_realtime_flops(self, cpu_percent: float, gpu_percent: float = 0) -> Dict[str, float]:
        """计算实时FLOPS
        
        基于使用率估算实际FLOPS:
        Actual FLOPS ≈ Peak FLOPS × (utilization / 100) × efficiency_factor
        
        Args:
            cpu_percent: CPU使用率 (0-100)
            gpu_percent: GPU使用率 (0-100)
            
        Returns:
            FLOPS指标字典
        """
        # 效率因子（实际性能通常是理论峰值的30-70%）
        efficiency = 0.5
        
        # CPU实时GFLOPS
        cpu_gflops = self.cpu_peak_gflops * (cpu_percent / 100) * efficiency
        
        # GPU实时GFLOPS
        gpu_gflops = self.gpu_peak_gflops * (gpu_percent / 100) * efficiency if gpu_percent > 0 else 0
        
        # 总GFLOPS
        total_gflops = cpu_gflops + gpu_gflops
        
        # 转换为TFLOPS
        total_tflops = total_gflops / 1000
        
        return {
            'cpu_gflops': round(cpu_gflops, 2),
            'gpu_gflops': round(gpu_gflops, 2),
            'total_gflops': round(total_gflops, 2),
            'total_tflops': round(total_tflops, 4),
            'cpu_peak_gflops': round(self.cpu_peak_gflops, 2),
            'gpu_peak_gflops': round(self.gpu_peak_gflops, 2),
        }
    
    def calculate_realtime_mips(self, cpu_percent: float) -> Dict[str, float]:
        """计算实时MIPS
        
        MIPS = Peak MIPS × (utilization / 100) × efficiency
        
        Args:
            cpu_percent: CPU使用率 (0-100)
            
        Returns:
            MIPS指标字典
        """
        efficiency = 0.6
        
        # 实时MIPS
        mips = self.cpu_peak_mips * (cpu_percent / 100) * efficiency
        
        # 转换为GIPS (Giga Instructions Per Second)
        gips = mips / 1000
        
        return {
            'mips': round(mips, 1),
            'gips': round(gips, 3),
            'peak_mips': round(self.cpu_peak_mips, 1),
        }
    
    def calculate_power(self, cpu_percent: float, gpu_percent: float = 0) -> Dict[str, float]:
        """计算功耗
        
        Power = TDP × (idle_factor + load_factor × utilization)
        
        Args:
            cpu_percent: CPU使用率
            gpu_percent: GPU使用率
            
        Returns:
            功耗指标字典
        """
        # CPU功耗（空闲约30% TDP）
        cpu_load = 0.3 + 0.7 * (cpu_percent / 100)
        cpu_power = self.specs.cpu_tdp * cpu_load
        
        # GPU功耗（空闲约10% TDP）
        if gpu_percent > 0:
            gpu_load = 0.1 + 0.9 * (gpu_percent / 100)
            gpu_power = self.specs.gpu_tdp * gpu_load
        else:
            gpu_power = 0
        
        # 总功耗
        total_power = cpu_power + gpu_power + self.specs.base_power
        
        return {
            'cpu_power_w': round(cpu_power, 1),
            'gpu_power_w': round(gpu_power, 1),
            'base_power_w': self.specs.base_power,
            'total_power_w': round(total_power, 1),
        }
    
    def update(self, cpu_percent: float, gpu_percent: float = 0, 
               interval_s: float = 1.0) -> Dict:
        """更新所有指标
        
        根据论文公式(12)：I = f_{T,D}(U(m|m ∈ UM))
        指标需要在时间(T)和数据(D)维度上进行标准化
        
        Args:
            cpu_percent: CPU使用率
            gpu_percent: GPU使用率
            interval_s: 采样间隔（秒）
            
        Returns:
            完整的指标字典
        """
        self._reset_daily_if_needed()
        
        current_time = datetime.now()
        
        # ========== Performance Indicators (UP) ==========
        
        # 实时FLOPS
        flops = self.calculate_realtime_flops(cpu_percent, gpu_percent)
        
        # 实时MIPS
        mips = self.calculate_realtime_mips(cpu_percent)
        
        # 累计FLOPS（GFLOPS × 秒 = Giga浮点运算数）
        self._total_flops += flops['total_gflops'] * interval_s
        
        # 累计指令数（MIPS × 秒 × 10^6 = 指令数）
        self._total_instructions += mips['mips'] * interval_s * 1e6
        
        # 获取数据增量
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        data_delta = 0
        if disk_io:
            disk_delta = disk_io.write_bytes - self._last_disk_write
            if disk_delta > 0:
                data_delta += disk_delta
            self._last_disk_write = disk_io.write_bytes
        
        if net_io:
            net_delta = net_io.bytes_sent - self._last_net_upload
            if net_delta > 0:
                data_delta += net_delta
            self._last_net_upload = net_io.bytes_sent
        
        self._total_data_bytes += data_delta
        self._total_time_s += interval_s
        
        # ========== Energy Indicators (UE) ==========
        
        power = self.calculate_power(cpu_percent, gpu_percent)
        
        # 累计能耗 (Wh)
        energy_delta = power['total_power_w'] * (interval_s / 3600)
        self._total_energy_wh += energy_delta
        
        # 碳排放 (g CO2)
        carbon_g = self._total_energy_wh / 1000 * self.CARBON_FACTOR * 1000
        
        # ========== Per-Unit-Data Indicators ==========
        # 根据论文，指标应该分配到单位数据
        
        data_mb = self._total_data_bytes / (1024 ** 2)
        
        if data_mb > 0:
            # TPD: Time Per unit Data (s/MB)
            tpd = self._total_time_s / data_mb
            
            # MPD: Million Instructions Per Data (MI/MB)
            mpd = (self._total_instructions / 1e6) / data_mb
            
            # WPD: Energy Per unit Data (Wh/MB)
            wpd = self._total_energy_wh / data_mb
            
            # CPD: Carbon Per unit Data (g CO2/MB)
            cpd = carbon_g / data_mb
            
            # FLOPS Per Data (GFLOPS·s/MB)
            fpd = self._total_flops / data_mb
        else:
            tpd = mpd = wpd = cpd = fpd = 0
        
        # ========== Effort Rate (ER) ==========
        # ER是综合成本指标，结合时间、能耗和计算资源
        # 论文建议：ER = f(TPD, WPD, MPD)
        # 简化实现：ER = α×TPD + β×WPD + γ×MPD (标准化后)
        
        # 标准化系数（可调整权重）
        alpha, beta, gamma = 0.3, 0.4, 0.3
        
        # 参考基准值（用于标准化）
        tpd_ref = 1.0      # 1 s/MB
        wpd_ref = 0.01     # 0.01 Wh/MB
        mpd_ref = 1000.0   # 1000 MI/MB
        
        if data_mb > 0:
            er = (
                alpha * (tpd / tpd_ref) + 
                beta * (wpd / wpd_ref) + 
                gamma * (mpd / mpd_ref)
            )
        else:
            er = 0
        
        # ========== DPU Efficiency ==========
        # 数据处理效率 = 数据量 / (能耗 × 时间)
        if self._total_energy_wh > 0 and self._total_time_s > 0:
            dpu_efficiency = data_mb / (self._total_energy_wh * self._total_time_s / 3600)
        else:
            dpu_efficiency = 0
        
        self._last_update = current_time
        
        return {
            # Performance Indicators
            'flops': flops,
            'mips': mips,
            'total_flops_gops': round(self._total_flops, 2),  # 累计GFLOPS·s
            'total_instructions_mi': round(self._total_instructions / 1e6, 2),  # 累计百万指令
            'data_generated_mb': round(data_mb, 2),
            'processing_time_s': round(self._total_time_s, 1),
            
            # Energy Indicators
            'power': power,
            'energy_wh': round(self._total_energy_wh, 3),
            'energy_kwh': round(self._total_energy_wh / 1000, 5),
            'carbon_g': round(carbon_g, 2),
            'carbon_kg': round(carbon_g / 1000, 4),
            
            # Per-Unit-Data Indicators (论文核心指标)
            'tpd': round(tpd, 4),      # s/MB
            'mpd': round(mpd, 2),      # MI/MB
            'wpd': round(wpd, 6),      # Wh/MB
            'cpd': round(cpd, 4),      # g CO2/MB
            'fpd': round(fpd, 4),      # GFLOPS·s/MB
            
            # Value Indicators
            'effort_rate': round(er, 4),
            'dpu_efficiency': round(dpu_efficiency, 4),
            
            # 系统信息
            'timestamp': current_time.isoformat(),
            'peak_gflops': round(self.total_peak_gflops, 2),
            'peak_mips': round(self.cpu_peak_mips, 1),
        }
    
    def get_summary(self) -> Dict:
        """获取今日摘要"""
        self._reset_daily_if_needed()
        
        data_mb = self._total_data_bytes / (1024 ** 2)
        carbon_g = self._total_energy_wh / 1000 * self.CARBON_FACTOR * 1000
        
        return {
            'date': self._today.isoformat(),
            
            # 累计性能
            'total_gflops_s': round(self._total_flops, 2),
            'total_instructions_billion': round(self._total_instructions / 1e9, 3),
            
            # 累计能耗
            'total_energy_wh': round(self._total_energy_wh, 2),
            'total_carbon_g': round(carbon_g, 1),
            
            # 累计数据
            'total_data_mb': round(data_mb, 2),
            'total_time_hours': round(self._total_time_s / 3600, 2),
            
            # 平均指标
            'avg_tpd': round(self._total_time_s / data_mb, 4) if data_mb > 0 else 0,
            'avg_wpd': round(self._total_energy_wh / data_mb, 6) if data_mb > 0 else 0,
            'avg_cpd': round(carbon_g / data_mb, 4) if data_mb > 0 else 0,
        }
    
    def get_hardware_info(self) -> Dict:
        """获取硬件信息"""
        return {
            'cpu_cores': self.specs.cpu_cores,
            'cpu_freq_ghz': self.specs.cpu_freq_ghz,
            'cpu_tdp_w': self.specs.cpu_tdp,
            'gpu_cores': self.specs.gpu_cores,
            'gpu_tdp_w': self.specs.gpu_tdp,
            'cpu_peak_gflops': round(self.cpu_peak_gflops, 2),
            'gpu_peak_gflops': round(self.gpu_peak_gflops, 2),
            'total_peak_gflops': round(self.total_peak_gflops, 2),
            'cpu_peak_mips': round(self.cpu_peak_mips, 1),
        }
