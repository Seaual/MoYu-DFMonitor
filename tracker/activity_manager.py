"""
活动追踪管理器
"""
from datetime import datetime
from typing import Dict, List, Optional, Callable

from .app_tracker import AppTracker
from .browser_tracker import BrowserTracker


class ActivityManager:
    """活动追踪管理器 - 整合应用和浏览器追踪"""
    
    def __init__(self):
        self.app_tracker = AppTracker()
        self.browser_tracker = BrowserTracker()
        
        # 事件回调
        self._on_app_switch: Optional[Callable] = None
        self._on_site_visit: Optional[Callable] = None
    
    def set_callbacks(self, 
                      on_app_switch: Optional[Callable] = None,
                      on_site_visit: Optional[Callable] = None):
        """设置事件回调
        
        Args:
            on_app_switch: 应用切换时的回调 callback(event_dict)
            on_site_visit: 网站访问时的回调 callback(event_dict)
        """
        self._on_app_switch = on_app_switch
        self._on_site_visit = on_site_visit
    
    def update(self) -> Dict:
        """更新追踪状态
        
        应该每秒调用一次
        
        Returns:
            包含事件信息的字典
        """
        result = {
            'app_event': None,
            'site_event': None,
            'current_app': None,
            'current_site': None
        }
        
        # 更新应用追踪
        app_event = self.app_tracker.update()
        if app_event:
            result['app_event'] = app_event
            if self._on_app_switch:
                self._on_app_switch(app_event)
        
        # 获取当前应用信息
        current_app = self.app_tracker.get_current_app()
        result['current_app'] = current_app
        
        # 更新浏览器追踪
        if current_app:
            site_event = self.browser_tracker.update(
                is_browser=current_app.get('is_browser', False),
                browser_name=current_app.get('friendly_name', ''),
                window_title=current_app.get('window_title', '')
            )
            if site_event:
                result['site_event'] = site_event
                if self._on_site_visit:
                    self._on_site_visit(site_event)
            
            result['current_site'] = self.browser_tracker.get_current_site()
        else:
            # 如果没有活动应用，清除浏览器状态
            self.browser_tracker.update(False, '', '')
        
        return result
    
    def get_app_usage(self) -> Dict[str, float]:
        """获取今日应用使用时长"""
        return self.app_tracker.get_daily_usage()
    
    def get_app_usage_sorted(self) -> List:
        """获取按时长排序的应用使用统计"""
        return self.app_tracker.get_daily_usage_sorted()
    
    def get_site_visits(self) -> Dict[str, float]:
        """获取今日网站访问时长"""
        return self.browser_tracker.get_daily_visits()
    
    def get_site_visits_sorted(self) -> List:
        """获取按时长排序的网站访问统计"""
        return self.browser_tracker.get_daily_visits_sorted()
    
    def get_app_log(self) -> List[Dict]:
        """获取应用活动记录"""
        return self.app_tracker.get_activity_log()
    
    def get_site_log(self) -> List[Dict]:
        """获取网站访问记录"""
        return self.browser_tracker.get_visit_log()
    
    def get_recent_sites(self, limit: int = 20) -> List[Dict]:
        """获取最近访问的网站"""
        return self.browser_tracker.get_recent_visits(limit)
    
    def get_current_status(self) -> Dict:
        """获取当前状态"""
        return {
            'current_app': self.app_tracker.get_current_app(),
            'current_site': self.browser_tracker.get_current_site()
        }
    
    def get_summary(self) -> Dict:
        """获取今日摘要"""
        app_usage = self.get_app_usage_sorted()
        site_visits = self.get_site_visits_sorted()
        
        total_app_time = sum(t for _, t in app_usage)
        total_site_time = sum(t for _, t in site_visits)
        
        return {
            'date': datetime.now().date().isoformat(),
            'total_app_time': total_app_time,
            'total_site_time': total_site_time,
            'app_count': len(app_usage),
            'site_count': len(site_visits),
            'top_apps': app_usage[:5],
            'top_sites': site_visits[:5]
        }
    
    @staticmethod
    def format_duration(seconds: float) -> str:
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
