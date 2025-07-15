import platform
import os
import sys
import ctypes
from win32api import GetFileVersionInfo, LOWORD, HIWORD

def get_system_info():
    """获取系统基本信息"""
    try:
        # 使用ctypes获取完整系统信息
        class OSVERSIONINFOEXW(ctypes.Structure):
            _fields_ = [
                ("dwOSVersionInfoSize", ctypes.c_ulong),
                ("dwMajorVersion", ctypes.c_ulong),
                ("dwMinorVersion", ctypes.c_ulong),
                ("dwBuildNumber", ctypes.c_ulong),
                ("dwPlatformId", ctypes.c_ulong),
                ("szCSDVersion", ctypes.c_wchar * 128),
                ("wServicePackMajor", ctypes.c_ushort),
                ("wServicePackMinor", ctypes.c_ushort),
                ("wSuiteMask", ctypes.c_ushort),
                ("wProductType", ctypes.c_byte),
                ("wReserved", ctypes.c_byte)
            ]
        
        ver = OSVERSIONINFOEXW()
        ver.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
        ctypes.windll.Ntdll.RtlGetVersion(ctypes.byref(ver))
        
        # 获取系统架构
        arch = "x64" if sys.maxsize > 2**32 else "x86"
        
        return {
            "os_name": "Windows",
            "os_version": f"{ver.dwMajorVersion}.{ver.dwMinorVersion}",
            "build": f"{ver.dwBuildNumber}",
            "arch": arch,
            "python_version": platform.python_version()
        }
    except Exception as e:
        print(f"获取系统信息失败: {str(e)}")
        # 返回最小化信息保证程序继续运行
        return {
            "os_name": "Windows",
            "os_version": "未知版本",
            "build": "未知构建",
            "arch": "未知架构",
            "python_version": platform.python_version()
        }

def get_windows_unicode_version():
    """通过Windows API获取精确的Unicode版本"""
    try:
        # 使用ctypes调用Windows API
        class OSVERSIONINFOEXW(ctypes.Structure):
            _fields_ = [
                ("dwOSVersionInfoSize", ctypes.c_ulong),
                ("dwMajorVersion", ctypes.c_ulong),
                ("dwMinorVersion", ctypes.c_ulong),
                ("dwBuildNumber", ctypes.c_ulong),
                ("dwPlatformId", ctypes.c_ulong),
                ("szCSDVersion", ctypes.c_wchar * 128),
                ("wServicePackMajor", ctypes.c_ushort),
                ("wServicePackMinor", ctypes.c_ushort),
                ("wSuiteMask", ctypes.c_ushort),
                ("wProductType", ctypes.c_byte),
                ("wReserved", ctypes.c_byte)
            ]
        
        ver = OSVERSIONINFOEXW()
        ver.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
        ctypes.windll.Ntdll.RtlGetVersion(ctypes.byref(ver))
        
        build_number = ver.dwBuildNumber
        
        # 根据构建号映射Unicode版本
        if build_number >= 22000:  # Windows 11
            return "15.1"
        elif build_number >= 19041:  # Windows 10 2004+
            return "14.0"
        elif build_number >= 14393:  # Windows 10 Anniversary Update
            return "12.1"
        else:
            return "12.0"
    except Exception as e:
        print(f"获取Unicode版本失败: {str(e)}")
        return "未知版本"

def get_segoe_emoji_version():
    """增强的字体检测 - 获取Segoe UI Emoji字体版本"""
    try:
        # Windows字体路径
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
        
        if os.path.exists(font_path):
            # 检查文件是否包含资源区域
            try:
                info = GetFileVersionInfo(font_path, '\\')
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                
                version = f"{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"
                
                # 根据主版本号返回简化版本
                if HIWORD(ms) >= 5:
                    return "5.00"
                elif HIWORD(ms) >= 3:
                    return "3.00"
                else:
                    return "1.51"
            except Exception as e:
                print(f"获取字体版本失败: {str(e)}")
                # 文件存在但无法获取版本信息时返回"未知版本"
                return "未知版本"
        else:
            return "未安装"
    except Exception as e:
        print(f"获取字体版本失败: {str(e)}")
        return "未知版本"

def get_segoe_font_name():
    """获取系统中安装的Segoe UI字体名称（支持Emoji/Symbol版本）"""
    try:
        import winreg
        
        # 注册表路径
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        
        # 打开注册表项
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            i = 0
            while True:
                try:
                    # 枚举所有键值
                    name, value, _ = winreg.EnumValue(key, i)
                    
                    # 查找Segoe UI相关字体
                    if "Segoe UI" in name:
                        # 移除(TrueType)标识
                        if " (" in name:
                            name = name.split(" (")[0]
                        
                        # 优先返回Emoji版本
                        if "Emoji" in name:
                            return name
                        
                        # 备选Symbol版本
                        if "Symbol" in name:
                            return name
                            
                    i += 1
                except OSError:
                    break
                    
        # 默认回退值
        return "Segoe UI Emoji"
        
    except Exception as e:
        print(f"获取Segoe字体失败: {str(e)}")
        return "Segoe UI Emoji"

def check_python_compatibility():
    """检查 Python 版本兼容性"""
    try:
        # 获取Python版本
        major, minor, patch = map(int, platform.python_version_tuple())
        
        # 检查与PySide6的兼容性
        if major != 3 or minor < 6 or minor > 11:
            return False, f"Python {major}.{minor} 不符合要求（需3.6-3.11）"
            
        # 检查与Windows版本的兼容性
        sys_info = get_system_info()
        if sys_info["os_name"] == "Windows":
            build = int(sys_info["build"].split('.')[-1])
            if build < 19041 and major >= 3 and minor >= 9:
                return False, "Python 3.9+ 需要 Windows 10 2004+ 或更高版本"
                
        return True, "兼容性检查通过"
    except Exception as e:
        print(f"兼容性检查失败: {str(e)}")
        return False, f"检查失败: {str(e)}"