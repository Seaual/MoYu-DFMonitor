# -*- coding: utf-8 -*-
"""
双语支持：中文 / English
在设置中可切换语言，偏好会持久化保存。
"""
import os

# 默认从 QSettings 读取，若未设置则用系统语言或中文
_CURRENT_LANG = "zh"

# 翻译表：key -> (中文, 英文)
_TRANSLATIONS = {
    # 应用与主窗口
    "app_name": ("摸鱼了么", "Slacking?"),
    "app_subtitle": ("PC数字足迹检测", "PC Digital Footprint"),
    "tip_close": ("关闭", "Close"),
    "tip_minimize": ("最小化", "Minimize"),
    "tip_maximize": ("最大化", "Maximize"),
    "btn_settings": ("设置", "Settings"),
    "tab_footprint": ("数字足迹", "Digital Footprint"),
    "tab_monitor": ("系统监控", "System Monitor"),
    "tab_activity": ("活动统计", "Activity"),
    "version": ("v1.0.0", "v1.0.0"),
    "autostart_on": ("● 开机自启动已启用", "● Auto-start enabled"),
    "autostart_off": ("○ 开机自启动未启用", "○ Auto-start disabled"),
    # 设置菜单
    "menu_autostart": ("🚀 开机自启动", "🚀 Auto-start"),
    "menu_export": ("📁 导出数据", "📁 Export Data"),
    "menu_about": ("ℹ️ 关于", "ℹ️ About"),
    "menu_exit": ("🚪 退出程序", "🚪 Quit"),
    "menu_show_window": ("显示窗口", "Show Window"),
    "menu_quit": ("退出", "Quit"),
    "menu_language": ("🌐 语言", "🌐 Language"),
    "lang_zh": ("中文", "Chinese"),
    "lang_en": ("English", "English"),
    # 消息与关于
    "msg_export_title": ("导出数据", "Export Data"),
    "msg_export_saved": ("数据已保存至:", "Data saved to:"),
    "msg_autostart_failed": ("启用开机自启动失败", "Failed to enable auto-start"),
    "about_desc": (
        "一款帮助你了解个人电脑资源消耗的工具。<br><br>"
        "监测 CPU、内存、GPU 使用率，追踪软件使用时长，"
        "计算能耗与碳排放，全面量化你的数字足迹。",
        "A tool to understand your PC resource usage.<br><br>"
        "Monitors CPU, memory, GPU usage; tracks app and web usage; "
        "calculates energy and carbon footprint."
    ),
    "about_refs": ("📚 参考文献:", "📚 References:"),
    "about_based": ("基于 Digitization Footprint (DF-LCA) 框架开发", "Based on DF-LCA framework"),
    # 系统监控 Tab
    "monitor_cpu": ("CPU", "CPU"),
    "monitor_memory": ("内存", "Memory"),
    "monitor_gpu": ("GPU", "GPU"),
    "monitor_vram": ("显存", "VRAM"),
    "monitor_trend": ("使用率趋势", "Usage Trend"),
    "monitor_legend_cpu": ("CPU", "CPU"),
    "monitor_legend_mem": ("内存", "Memory"),
    "monitor_legend_gpu": ("GPU", "GPU"),
    "monitor_freq": ("CPU 频率", "CPU Freq"),
    "monitor_mem_use": ("内存使用", "Memory"),
    "monitor_disk_read": ("磁盘读取", "Disk Read"),
    "monitor_disk_write": ("磁盘写入", "Disk Write"),
    "monitor_net_up": ("网络上传", "Upload"),
    "monitor_net_down": ("网络下载", "Download"),
    "monitor_gpu_ok": ("✅ GPU 已连接", "✅ GPU connected"),
    "monitor_gpu_none": ("⚪ GPU 未检测到", "⚪ No GPU"),
    "monitor_interval": ("采样间隔", "Interval"),
    "monitor_interval_1": ("1 秒", "1 s"),
    "monitor_interval_2": ("2 秒", "2 s"),
    "monitor_interval_5": ("5 秒", "5 s"),
    "monitor_record_start": ("🔴 开始记录", "🔴 Start Record"),
    "monitor_record_stop": ("⏹️ 停止记录", "⏹️ Stop Record"),
    # 活动统计 Tab
    "activity_current_browse": ("当前浏览", "Current"),
    "activity_duration": ("持续", "Duration"),
    "activity_today_summary": ("今日摘要", "Today Summary"),
    "activity_usage_time": ("使用时长", "Usage"),
    "activity_app_count": ("应用数量", "Apps"),
    "activity_site_count": ("网站数量", "Sites"),
    "activity_time_dist": ("今日使用时间分布", "Today Usage by Hour"),
    "activity_by_hour": ("按小时统计", "By hour"),
    "activity_app_ranking": ("应用使用时长排行", "App Usage Ranking"),
    "activity_site_ranking": ("网站访问时长排行", "Site Visit Ranking"),
    "activity_usage_mins": ("使用时长 (分钟)", "Usage (min)"),
    "activity_visit_mins": ("访问时长 (分钟)", "Visit (min)"),
    "activity_timeline_ylabel": ("使用时长 (分钟)", "Usage (min)"),
    "activity_hours_mins": ("{hours}小时{mins}分", "{hours}h {mins}m"),
    # 数字足迹 Tab
    "fp_hello": ("👋 你好，欢迎回来", "👋 Hello, welcome back"),
    "fp_today_date": ("%Y年%m月%d日", "%b %d, %Y"),
    "fp_today_summary_desc": ("📊 以下是你今天的数字足迹摘要", "📊 Your today's digital footprint summary"),
    "fp_energy_wh": ("Wh 能耗", "Wh Energy"),
    "fp_carbon": ("g CO₂", "g CO₂"),
    "fp_realtime": ("实时性能", "Realtime"),
    "fp_compute": ("计算性能", "Compute"),
    "fp_instructions": ("指令执行", "Instructions"),
    "fp_power": ("实时功耗", "Power"),
    "fp_data_gen": ("数据生成", "Data Gen"),
    "fp_per_unit": ("单位数据指标 (Per-Unit-Data)", "Per-Unit-Data"),
    "fp_tpd": ("TPD", "TPD"),
    "fp_mpd": ("MPD", "MPD"),
    "fp_wpd": ("WPD", "WPD"),
    "fp_cpd": ("CPD", "CPD"),
    "fp_effort": ("Effort", "Effort"),
    "fp_trend": ("性能趋势", "Performance Trend"),
    "fp_legend_power": ("功耗", "Power"),
    "fp_legend_gflops": ("GFLOPS", "GFLOPS"),
    "fp_storage": ("存储空间", "Storage"),
    "fp_used": ("已使用", "Used"),
    "fp_disk_partition": ("分区", "Partition"),
    "fp_disk_used": ("已用", "Used"),
    "fp_disk_usage": ("使用率", "Usage"),
    "fp_disk_used_format": ("已使用 {used:.0f} GB / {total:.0f} GB", "Used {used:.0f} GB / {total:.0f} GB"),
    "fp_mb_today": ("MB 今日", "MB today"),
    "fp_effort_unit": ("综合成本", "Effort"),
    "fp_formula_intro": ("📝 DF-LCA 公式  ", "📝 DF-LCA  "),
    "fp_formula_tpd": ("TPD", "TPD"),
    "fp_formula_tpd_eq": (" = Time÷Data  ", " = Time÷Data  "),
    "fp_formula_mpd": ("MPD", "MPD"),
    "fp_formula_mpd_eq": (" = Instructions÷Data  ", " = Instructions÷Data  "),
    "fp_formula_wpd": ("WPD", "WPD"),
    "fp_formula_wpd_eq": (" = Energy÷Data  ", " = Energy÷Data  "),
    "fp_formula_cpd": ("CPD", "CPD"),
    "fp_formula_cpd_eq": (" = Carbon÷Data  ", " = Carbon÷Data  "),
    "fp_formula_er": ("ER", "ER"),
    "fp_formula_er_eq": (" = α·TPD + β·WPD + γ·MPD", " = α·TPD + β·WPD + γ·MPD"),
}


def _get_settings():
    try:
        from PyQt5.QtCore import QSettings
        return QSettings("DFMonitor", "DFMonitor")
    except Exception:
        return None


def current_language():
    """当前语言: 'zh' 或 'en'"""
    global _CURRENT_LANG
    s = _get_settings()
    if s is not None:
        lang = s.value("language", "zh")
        if lang in ("zh", "en"):
            _CURRENT_LANG = lang
    return _CURRENT_LANG


def set_language(lang: str) -> bool:
    """设置语言并持久化。lang 为 'zh' 或 'en'。返回是否成功。"""
    global _CURRENT_LANG
    if lang not in ("zh", "en"):
        return False
    _CURRENT_LANG = lang
    s = _get_settings()
    if s is not None:
        s.setValue("language", lang)
    return True


def _(key: str) -> str:
    """根据当前语言返回对应文案。"""
    if key not in _TRANSLATIONS:
        return key
    pair = _TRANSLATIONS[key]
    return pair[0] if current_language() == "zh" else pair[1]


def init_language():
    """应用启动时调用，从设置中加载语言。"""
    current_language()
