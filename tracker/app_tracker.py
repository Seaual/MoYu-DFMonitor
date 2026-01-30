"""
应用程序使用时长追踪模块
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict

try:
    import win32gui
    import win32process
    import psutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class AppTracker:
    """应用程序使用时长追踪器"""
    
    # 常见浏览器进程名
    BROWSERS = {
        'chrome.exe': 'Chrome',
        'msedge.exe': 'Edge', 
        'firefox.exe': 'Firefox',
        'opera.exe': 'Opera',
        'brave.exe': 'Brave',
        'iexplore.exe': 'IE',
        '360se.exe': '360浏览器',
        'qqbrowser.exe': 'QQ浏览器',
        'sogouexplorer.exe': '搜狗浏览器'
    }
    
    def __init__(self):
        self.available = WIN32_AVAILABLE
        self._current_app = None
        self._current_title = None
        self._app_start_time = None
        
        # 今日使用时长统计 {app_name: total_seconds}
        self._daily_usage: Dict[str, float] = defaultdict(float)
        self._today = datetime.now().date()
        
        # 活动记录列表 [(timestamp, app_name, window_title, duration)]
        self._activity_log = []
    
    def _reset_daily_if_needed(self):
        """如果跨天则重置统计"""
        today = datetime.now().date()
        if today != self._today:
            self._daily_usage.clear()
            self._activity_log.clear()
            self._today = today
    
    def get_active_window_info(self) -> Optional[Tuple[str, str]]:
        """获取当前活动窗口信息
        
        Returns:
            (进程名, 窗口标题) 或 None
        """
        if not self.available:
            return None
        
        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            
            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # 获取进程名
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            return (process_name, window_title)
        
        except Exception:
            return None
    
    def is_browser(self, process_name: str) -> bool:
        """判断是否是浏览器"""
        return process_name.lower() in self.BROWSERS
    
    def get_browser_name(self, process_name: str) -> Optional[str]:
        """获取浏览器友好名称"""
        return self.BROWSERS.get(process_name.lower())
    
    def get_friendly_app_name(self, process_name: str) -> str:
        """获取应用程序友好名称"""
        # 常见应用的友好名称映射
        app_names = {
            'code.exe': 'VS Code',
            'devenv.exe': 'Visual Studio',
            'pycharm64.exe': 'PyCharm',
            'idea64.exe': 'IntelliJ IDEA',
            'notepad.exe': '记事本',
            'notepad++.exe': 'Notepad++',
            'explorer.exe': '文件资源管理器',
            'wechat.exe': '微信',
            'qq.exe': 'QQ',
            'dingtalk.exe': '钉钉',
            'feishu.exe': '飞书',
            'tim.exe': 'TIM',
            'windowsterminal.exe': 'Windows Terminal',
            'powershell.exe': 'PowerShell',
            'cmd.exe': '命令提示符',
            'excel.exe': 'Excel',
            'winword.exe': 'Word',
            'powerpnt.exe': 'PowerPoint',
            'onenote.exe': 'OneNote',
            'outlook.exe': 'Outlook',
            'spotify.exe': 'Spotify',
            'cloudmusic.exe': '网易云音乐',
            'qqmusic.exe': 'QQ音乐',
            'potplayermini64.exe': 'PotPlayer',
            'vlc.exe': 'VLC',
        }
        
        name_lower = process_name.lower()
        
        # 检查浏览器
        if name_lower in self.BROWSERS:
            return self.BROWSERS[name_lower]
        
        # 检查常见应用
        if name_lower in app_names:
            return app_names[name_lower]
        
        # 返回去掉.exe的进程名
        if name_lower.endswith('.exe'):
            return process_name[:-4]
        
        return process_name
    
    def update(self) -> Optional[Dict]:
        """更新追踪状态，返回切换事件信息
        
        应该每秒调用一次
        
        Returns:
            如果发生应用切换，返回切换事件信息，否则返回None
        """
        self._reset_daily_if_needed()
        
        window_info = self.get_active_window_info()
        if not window_info:
            return None
        
        process_name, window_title = window_info
        current_time = datetime.now()
        
        # 检查是否切换了应用
        if process_name != self._current_app or window_title != self._current_title:
            event = None
            
            # 如果之前有活动应用，记录其使用时长
            if self._current_app and self._app_start_time:
                duration = (current_time - self._app_start_time).total_seconds()
                if duration > 0:
                    # 更新统计
                    friendly_name = self.get_friendly_app_name(self._current_app)
                    self._daily_usage[friendly_name] += duration
                    
                    # 记录活动
                    event = {
                        'timestamp': self._app_start_time.isoformat(),
                        'end_time': current_time.isoformat(),
                        'app_name': self._current_app,
                        'friendly_name': friendly_name,
                        'window_title': self._current_title,
                        'duration': duration,
                        'is_browser': self.is_browser(self._current_app)
                    }
                    self._activity_log.append(event)
            
            # 更新当前应用
            self._current_app = process_name
            self._current_title = window_title
            self._app_start_time = current_time
            
            return event
        
        return None
    
    def get_current_app(self) -> Optional[Dict]:
        """获取当前活动应用信息"""
        if not self._current_app:
            return None
        
        duration = 0
        if self._app_start_time:
            duration = (datetime.now() - self._app_start_time).total_seconds()
        
        return {
            'app_name': self._current_app,
            'friendly_name': self.get_friendly_app_name(self._current_app),
            'window_title': self._current_title,
            'duration': duration,
            'is_browser': self.is_browser(self._current_app)
        }
    
    def get_daily_usage(self) -> Dict[str, float]:
        """获取今日应用使用时长统计
        
        Returns:
            {应用友好名称: 使用秒数}
        """
        self._reset_daily_if_needed()
        
        # 加上当前正在使用的应用时长
        result = dict(self._daily_usage)
        
        if self._current_app and self._app_start_time:
            friendly_name = self.get_friendly_app_name(self._current_app)
            current_duration = (datetime.now() - self._app_start_time).total_seconds()
            result[friendly_name] = result.get(friendly_name, 0) + current_duration
        
        return result
    
    def get_daily_usage_sorted(self) -> list:
        """获取按使用时长排序的今日统计
        
        Returns:
            [(应用名, 使用秒数), ...] 按时长降序
        """
        usage = self.get_daily_usage()
        return sorted(usage.items(), key=lambda x: x[1], reverse=True)
    
    def get_activity_log(self) -> list:
        """获取今日活动记录"""
        self._reset_daily_if_needed()
        return list(self._activity_log)
    
    def format_duration(self, seconds: float) -> str:
        """格式化时长显示"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分"
