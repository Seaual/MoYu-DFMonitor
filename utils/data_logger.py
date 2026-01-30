"""
数据记录模块 - CSV格式
"""
import os
import csv
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class DataLogger:
    """数据记录器"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化数据记录器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.system_dir = self.data_dir / "system"
        self.activity_dir = self.data_dir / "activity"
        
        # 确保目录存在
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.activity_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前日期和文件句柄
        self._current_date = None
        self._system_file = None
        self._system_writer = None
        self._app_file = None
        self._app_writer = None
        self._web_file = None
        self._web_writer = None
    
    def _get_date_str(self) -> str:
        """获取当前日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _check_date_change(self):
        """检查是否跨天，如果是则重新打开文件"""
        current_date = self._get_date_str()
        if current_date != self._current_date:
            self._close_files()
            self._current_date = current_date
    
    def _close_files(self):
        """关闭所有打开的文件"""
        if self._system_file:
            self._system_file.close()
            self._system_file = None
            self._system_writer = None
        if self._app_file:
            self._app_file.close()
            self._app_file = None
            self._app_writer = None
        if self._web_file:
            self._web_file.close()
            self._web_file = None
            self._web_writer = None
    
    def _get_system_writer(self):
        """获取系统监控CSV写入器"""
        self._check_date_change()
        
        if self._system_writer is None:
            filepath = self.system_dir / f"monitor_{self._current_date}.csv"
            file_exists = filepath.exists()
            
            self._system_file = open(filepath, 'a', newline='', encoding='utf-8')
            self._system_writer = csv.writer(self._system_file)
            
            # 如果是新文件，写入表头
            if not file_exists:
                self._system_writer.writerow([
                    'timestamp', 'cpu_percent', 'memory_percent',
                    'gpu_percent', 'gpu_memory_percent',
                    'disk_read_speed', 'disk_write_speed',
                    'net_sent_speed', 'net_recv_speed'
                ])
                self._system_file.flush()
        
        return self._system_writer
    
    def _get_app_writer(self):
        """获取应用使用CSV写入器"""
        self._check_date_change()
        
        if self._app_writer is None:
            filepath = self.activity_dir / f"app_usage_{self._current_date}.csv"
            file_exists = filepath.exists()
            
            self._app_file = open(filepath, 'a', newline='', encoding='utf-8')
            self._app_writer = csv.writer(self._app_file)
            
            if not file_exists:
                self._app_writer.writerow([
                    'timestamp', 'end_time', 'app_name', 'friendly_name',
                    'window_title', 'duration_seconds', 'is_browser'
                ])
                self._app_file.flush()
        
        return self._app_writer
    
    def _get_web_writer(self):
        """获取网站访问CSV写入器"""
        self._check_date_change()
        
        if self._web_writer is None:
            filepath = self.activity_dir / f"web_visits_{self._current_date}.csv"
            file_exists = filepath.exists()
            
            self._web_file = open(filepath, 'a', newline='', encoding='utf-8')
            self._web_writer = csv.writer(self._web_file)
            
            if not file_exists:
                self._web_writer.writerow([
                    'timestamp', 'end_time', 'browser', 'site_title', 'duration_seconds'
                ])
                self._web_file.flush()
        
        return self._web_writer
    
    def log_system_snapshot(self, snapshot: Dict):
        """记录系统监控快照
        
        Args:
            snapshot: SystemMonitor.get_snapshot() 返回的数据
        """
        writer = self._get_system_writer()
        
        disk_io = snapshot.get('disk_io', {})
        net_io = snapshot.get('network_io', {})
        
        writer.writerow([
            snapshot.get('timestamp', datetime.now().isoformat()),
            round(snapshot.get('cpu_percent', 0), 1),
            round(snapshot.get('memory_percent', 0), 1),
            round(snapshot.get('gpu_percent', 0), 1),
            round(snapshot.get('gpu_memory_percent', 0), 1),
            round(disk_io.get('read_speed', 0), 2),
            round(disk_io.get('write_speed', 0), 2),
            round(net_io.get('sent_speed', 0), 2),
            round(net_io.get('recv_speed', 0), 2)
        ])
        self._system_file.flush()
    
    def log_app_event(self, event: Dict):
        """记录应用切换事件
        
        Args:
            event: AppTracker 返回的事件数据
        """
        if not event:
            return
        
        writer = self._get_app_writer()
        
        writer.writerow([
            event.get('timestamp', ''),
            event.get('end_time', ''),
            event.get('app_name', ''),
            event.get('friendly_name', ''),
            event.get('window_title', ''),
            round(event.get('duration', 0), 1),
            event.get('is_browser', False)
        ])
        self._app_file.flush()
    
    def log_web_event(self, event: Dict):
        """记录网站访问事件
        
        Args:
            event: BrowserTracker 返回的事件数据
        """
        if not event:
            return
        
        writer = self._get_web_writer()
        
        writer.writerow([
            event.get('timestamp', ''),
            event.get('end_time', ''),
            event.get('browser', ''),
            event.get('site_title', ''),
            round(event.get('duration', 0), 1)
        ])
        self._web_file.flush()
    
    def read_system_data(self, date_str: Optional[str] = None) -> List[Dict]:
        """读取系统监控数据
        
        Args:
            date_str: 日期字符串，默认今天
            
        Returns:
            数据列表
        """
        if date_str is None:
            date_str = self._get_date_str()
        
        filepath = self.system_dir / f"monitor_{date_str}.csv"
        if not filepath.exists():
            return []
        
        result = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result.append(row)
        return result
    
    def read_app_data(self, date_str: Optional[str] = None) -> List[Dict]:
        """读取应用使用数据"""
        if date_str is None:
            date_str = self._get_date_str()
        
        filepath = self.activity_dir / f"app_usage_{date_str}.csv"
        if not filepath.exists():
            return []
        
        result = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result.append(row)
        return result
    
    def read_web_data(self, date_str: Optional[str] = None) -> List[Dict]:
        """读取网站访问数据"""
        if date_str is None:
            date_str = self._get_date_str()
        
        filepath = self.activity_dir / f"web_visits_{date_str}.csv"
        if not filepath.exists():
            return []
        
        result = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result.append(row)
        return result
    
    def get_available_dates(self) -> List[str]:
        """获取有数据的日期列表"""
        dates = set()
        
        # 从系统监控文件获取日期
        for f in self.system_dir.glob("monitor_*.csv"):
            date_str = f.stem.replace("monitor_", "")
            dates.add(date_str)
        
        # 从活动记录文件获取日期
        for f in self.activity_dir.glob("app_usage_*.csv"):
            date_str = f.stem.replace("app_usage_", "")
            dates.add(date_str)
        
        return sorted(dates, reverse=True)
    
    def close(self):
        """关闭所有文件"""
        self._close_files()
    
    def __del__(self):
        """析构函数"""
        self.close()
