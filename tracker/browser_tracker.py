"""
浏览器网站访问追踪模块
"""
import re
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class BrowserTracker:
    """浏览器网站访问追踪器"""
    
    # 浏览器窗口标题后缀模式
    BROWSER_SUFFIXES = [
        ' - Google Chrome',
        ' - Mozilla Firefox', 
        ' - Microsoft Edge',
        ' - Opera',
        ' - Brave',
        ' - Internet Explorer',
        ' - 360安全浏览器',
        ' - 360极速浏览器',
        ' - QQ浏览器',
        ' - 搜狗浏览器',
        ' and more',  # Chrome多标签
    ]
    
    def __init__(self):
        self._current_site = None
        self._current_browser = None
        self._site_start_time = None
        
        # 今日网站访问统计 {site_title: total_seconds}
        self._daily_visits: Dict[str, float] = defaultdict(float)
        self._today = datetime.now().date()
        
        # 访问记录列表
        self._visit_log: List[Dict] = []
    
    def _reset_daily_if_needed(self):
        """如果跨天则重置统计"""
        today = datetime.now().date()
        if today != self._today:
            self._daily_visits.clear()
            self._visit_log.clear()
            self._today = today
    
    def extract_site_title(self, window_title: str, browser_name: str) -> Optional[str]:
        """从浏览器窗口标题中提取网站标题
        
        Args:
            window_title: 窗口标题
            browser_name: 浏览器名称
            
        Returns:
            网站标题或None
        """
        if not window_title:
            return None
        
        title = window_title.strip()
        
        # 移除浏览器后缀
        for suffix in self.BROWSER_SUFFIXES:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
                break
        
        # 如果标题为空或只是浏览器名
        if not title or title.lower() in ['新标签页', 'new tab', '空白页']:
            return None
        
        # 清理一些常见的标题前缀/后缀
        # 例如 "(3) GitHub" -> "GitHub"
        title = re.sub(r'^\(\d+\)\s*', '', title)
        
        return title if title else None
    
    def update(self, is_browser: bool, browser_name: str, window_title: str) -> Optional[Dict]:
        """更新网站访问追踪
        
        Args:
            is_browser: 当前是否是浏览器窗口
            browser_name: 浏览器名称
            window_title: 窗口标题
            
        Returns:
            如果发生网站切换，返回访问事件信息
        """
        self._reset_daily_if_needed()
        
        current_time = datetime.now()
        
        if is_browser:
            site_title = self.extract_site_title(window_title, browser_name)
        else:
            site_title = None
        
        # 检查是否切换了网站
        if site_title != self._current_site or browser_name != self._current_browser:
            event = None
            
            # 如果之前在浏览网站，记录访问时长
            if self._current_site and self._site_start_time:
                duration = (current_time - self._site_start_time).total_seconds()
                if duration > 1:  # 至少访问1秒才记录
                    # 更新统计
                    self._daily_visits[self._current_site] += duration
                    
                    # 记录访问
                    event = {
                        'timestamp': self._site_start_time.isoformat(),
                        'end_time': current_time.isoformat(),
                        'browser': self._current_browser,
                        'site_title': self._current_site,
                        'duration': duration
                    }
                    self._visit_log.append(event)
            
            # 更新当前状态
            self._current_site = site_title
            self._current_browser = browser_name if is_browser else None
            self._site_start_time = current_time if site_title else None
            
            return event
        
        return None
    
    def get_current_site(self) -> Optional[Dict]:
        """获取当前访问的网站"""
        if not self._current_site:
            return None
        
        duration = 0
        if self._site_start_time:
            duration = (datetime.now() - self._site_start_time).total_seconds()
        
        return {
            'browser': self._current_browser,
            'site_title': self._current_site,
            'duration': duration
        }
    
    def get_daily_visits(self) -> Dict[str, float]:
        """获取今日网站访问时长统计
        
        Returns:
            {网站标题: 访问秒数}
        """
        self._reset_daily_if_needed()
        
        result = dict(self._daily_visits)
        
        # 加上当前正在访问的网站时长
        if self._current_site and self._site_start_time:
            current_duration = (datetime.now() - self._site_start_time).total_seconds()
            result[self._current_site] = result.get(self._current_site, 0) + current_duration
        
        return result
    
    def get_daily_visits_sorted(self) -> list:
        """获取按访问时长排序的今日统计
        
        Returns:
            [(网站标题, 访问秒数), ...] 按时长降序
        """
        visits = self.get_daily_visits()
        return sorted(visits.items(), key=lambda x: x[1], reverse=True)
    
    def get_visit_log(self) -> List[Dict]:
        """获取今日访问记录"""
        self._reset_daily_if_needed()
        return list(self._visit_log)
    
    def get_recent_visits(self, limit: int = 20) -> List[Dict]:
        """获取最近的访问记录
        
        Args:
            limit: 返回记录数量限制
        """
        self._reset_daily_if_needed()
        
        # 返回最近的记录
        log = self._visit_log[-limit:] if len(self._visit_log) > limit else self._visit_log
        
        # 如果当前正在访问网站，添加到结果中
        current = self.get_current_site()
        if current:
            current['timestamp'] = self._site_start_time.isoformat()
            current['end_time'] = None  # 正在进行中
            log = log + [current]
        
        return log
