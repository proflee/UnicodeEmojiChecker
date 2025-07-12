import platform
import ctypes
import re
import os

def get_system_info():
    """获取系统信息"""
    info = {
        "os_name": platform.system(),
        "os_version": platform.release(),
        "build": platform.version(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
    }
    return info

def get_windows_unicode_version():
    """通过Windows API获取精确的Unicode版本"""
    # 实现与原代码相同
    pass

def get_segoe_emoji_version():
    """增强的字体检测"""
    # 实现与原代码相同
    pass

def check_python_compatibility():
    """检查 Python 版本兼容性"""
    if platform.system() == "Windows":
        if platform.release() in ['7', '8'] and sys.version_info >= (3, 9):
            return False
    return True