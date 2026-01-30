"""
开机自启动工具模块
"""
import os
import sys
from pathlib import Path

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False


class AutoStart:
    """开机自启动管理器"""
    
    APP_NAME = "DFMonitor"
    
    def __init__(self):
        self.available = WINREG_AVAILABLE and sys.platform == 'win32'
    
    def _get_startup_folder(self) -> Path:
        """获取启动文件夹路径"""
        startup = Path(os.environ.get('APPDATA', '')) / \
                  'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        return startup
    
    def _get_shortcut_path(self) -> Path:
        """获取快捷方式路径"""
        return self._get_startup_folder() / f"{self.APP_NAME}.lnk"
    
    def _get_exe_path(self) -> str:
        """获取可执行文件路径"""
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的exe
            return sys.executable
        else:
            # Python脚本
            return sys.executable
    
    def _get_script_path(self) -> str:
        """获取主脚本路径"""
        # 假设main.py在项目根目录
        return str(Path(__file__).parent.parent / "main.py")
    
    def is_enabled(self) -> bool:
        """检查是否已启用开机自启动"""
        if not self.available:
            return False
        
        # 方法1: 检查启动文件夹
        shortcut_path = self._get_shortcut_path()
        if shortcut_path.exists():
            return True
        
        # 方法2: 检查注册表
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def enable_via_registry(self) -> bool:
        """通过注册表启用开机自启动"""
        if not self.available:
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # 构建启动命令
            if getattr(sys, 'frozen', False):
                # 打包后的exe
                command = f'"{self._get_exe_path()}"'
            else:
                # Python脚本
                command = f'"{self._get_exe_path()}" "{self._get_script_path()}"'
            
            winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            return True
        
        except Exception as e:
            print(f"启用自启动失败: {e}")
            return False
    
    def disable_via_registry(self) -> bool:
        """通过注册表禁用开机自启动"""
        if not self.available:
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, self.APP_NAME)
            except FileNotFoundError:
                pass  # 值不存在，无需删除
            
            winreg.CloseKey(key)
            return True
        
        except Exception as e:
            print(f"禁用自启动失败: {e}")
            return False
    
    def enable_via_shortcut(self) -> bool:
        """通过启动文件夹快捷方式启用开机自启动"""
        if not self.available:
            return False
        
        try:
            # 需要pywin32的shell模块
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(self._get_shortcut_path()))
            
            if getattr(sys, 'frozen', False):
                shortcut.Targetpath = self._get_exe_path()
            else:
                shortcut.Targetpath = self._get_exe_path()
                shortcut.Arguments = f'"{self._get_script_path()}"'
            
            shortcut.WorkingDirectory = str(Path(__file__).parent.parent)
            shortcut.IconLocation = self._get_exe_path()
            shortcut.save()
            
            return True
        
        except Exception as e:
            print(f"创建快捷方式失败: {e}")
            return False
    
    def disable_via_shortcut(self) -> bool:
        """删除启动文件夹中的快捷方式"""
        try:
            shortcut_path = self._get_shortcut_path()
            if shortcut_path.exists():
                shortcut_path.unlink()
            return True
        except Exception as e:
            print(f"删除快捷方式失败: {e}")
            return False
    
    def enable(self) -> bool:
        """启用开机自启动（推荐使用注册表方式）"""
        return self.enable_via_registry()
    
    def disable(self) -> bool:
        """禁用开机自启动"""
        # 同时清理两种方式
        result1 = self.disable_via_registry()
        result2 = self.disable_via_shortcut()
        return result1 or result2
    
    def toggle(self) -> bool:
        """切换开机自启动状态
        
        Returns:
            切换后的状态
        """
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True
