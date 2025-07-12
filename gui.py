import tkinter as tk
import os
import re
from tkinter import ttk, messagebox
from unicode_checker import UnicodeChecker
from utils import get_system_info, get_windows_unicode_version, get_segoe_emoji_version
import platform
import ctypes
from ctypes import wintypes

from config import UNICODE_TEST_CHARS

# 兼容性增强：处理不同Windows版本的字体名称差异
def get_segoe_font_name():
    """获取当前系统使用的表情符号字体名称"""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        )
        
        # 尝试可能的字体名称
        font_names = [
            "Segoe UI Emoji (TrueType)",
            "Segoe UI Symbol (TrueType)",
            "Segoe UI Historic (TrueType)",
            "Segoe MDL2 Assets (TrueType)"
        ]
        
        for name in font_names:
            try:
                winreg.QueryValueEx(key, name)
                return name
            except FileNotFoundError:
                continue
        
        return None
    except Exception:
        return None
# 兼容性增强：处理Windows 7缺少的API
def safe_get_windows_version():
    """安全获取Windows版本信息"""
    try:
        class OSVERSIONINFOEXW(ctypes.Structure):
            _fields_ = [
                ("dwOSVersionInfoSize", wintypes.DWORD),
                ("dwMajorVersion", wintypes.DWORD),
                ("dwMinorVersion", wintypes.DWORD),
                ("dwBuildNumber", wintypes.DWORD),
                ("dwPlatformId", wintypes.DWORD),
                ("szCSDVersion", wintypes.WCHAR * 128),
                ("wServicePackMajor", wintypes.WORD),
                ("wServicePackMinor", wintypes.WORD),
                ("wSuiteMask", wintypes.WORD),
                ("wProductType", wintypes.BYTE),
                ("wReserved", wintypes.BYTE)
            ]
        
        os_version = OSVERSIONINFOEXW()
        os_version.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
        
        # 使用更兼容的函数名
        if hasattr(ctypes.windll.ntdll, 'RtlGetVersion'):
            ctypes.windll.ntdll.RtlGetVersion(ctypes.byref(os_version))
        elif hasattr(ctypes.windll.kernel32, 'GetVersionExW'):
            ctypes.windll.kernel32.GetVersionExW(ctypes.byref(os_version))
        else:
            return None
        
        return os_version
    except Exception:
        return None

class UnicodeCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unicode 版本检测工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 设置应用图标
        try:
            self.root.iconbitmap("unicode.ico")
        except:
            pass

        # 创建样式
        self.setup_styles()

        # 创建界面组件
        self.create_widgets()

        # 开始检测
        self.detect_unicode_info()

    def detect_unicode_info(self):
        """检测Unicode信息"""
        self.status_var.set("正在检测系统信息...")
        self.root.update()

        # 获取系统信息
        sys_info = self.get_system_info()
        self.os_label.config(text=f"操作系统: {sys_info['os_name']} {sys_info['os_version']}")
        self.build_label.config(text=f"构建版本: {sys_info['build']}")
        self.arch_label.config(text=f"系统架构: {sys_info['arch']}")
        self.python_label.config(text=f"Python 版本: {sys_info['python_version']}")

        # 获取API检测结果
        self.status_var.set("正在通过系统API检测Unicode版本...")
        self.root.update()
        api_result = self.get_windows_unicode_version()
        self.api_result.config(text=api_result)

        # 获取字体检测结果
        self.status_var.set("正在检测Segoe UI Emoji字体版本...")
        self.root.update()
        font_result = self.get_segoe_emoji_version()
        self.font_result.config(text=font_result)

        # 测试字符支持
        self.status_var.set("正在测试Unicode字符支持...")
        self.root.update()
        test_results, max_supported = self.test_unicode_support()
        self.support_result.config(text=max_supported)

        # 填充表格
        for result in sorted(test_results, key=lambda x: float(x["version"]), reverse=True):
            version = result["version"]
            char = result["char"]
            status = result["status"]
            name = result["name"]
            release = result["release_date"]

            status_tag = "supported" if "✓" in status else "unsupported"

            self.tree.insert("", "end", values=(version, char, status, name, release), tags=(status_tag,))

        # 设置行样式
        self.tree.tag_configure("supported", background="#e8f5e9")
        self.tree.tag_configure("unsupported", background="#ffebee")

        self.status_var.set("检测完成")

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50", padding=10)
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#3498db", padding=(10, 5, 0, 5))
        style.configure("Result.TLabel", font=("Segoe UI", 10), padding=(5, 2, 5, 2))
        style.configure("Treeview", font=("Segoe UI", 9))

    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Unicode 版本检测工具", style="Title.TLabel")
        title_label.pack(fill=tk.X)

        sys_frame = ttk.LabelFrame(main_frame, text="系统信息", padding=10)
        sys_frame.pack(fill=tk.X, padx=5, pady=5)

        self.os_label = ttk.Label(sys_frame, text="操作系统: 检测中...", style="Result.TLabel")
        self.os_label.grid(row=0, column=0, sticky=tk.W)

        self.build_label = ttk.Label(sys_frame, text="构建版本: 检测中...", style="Result.TLabel")
        self.build_label.grid(row=0, column=1, sticky=tk.W)
        
        self.arch_label = ttk.Label(sys_frame, text="系统架构: 检测中...", style="Result.TLabel")
        self.arch_label.grid(row=1, column=0, sticky=tk.W)
        
        self.python_label = ttk.Label(sys_frame, text="Python 版本: 检测中...", style="Result.TLabel")
        self.python_label.grid(row=1, column=1, sticky=tk.W)
        
        # 检测结果框架
        result_frame = ttk.LabelFrame(main_frame, text="检测结果", padding=10)
        result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # API检测结果
        api_frame = ttk.Frame(result_frame)
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="系统 API 检测:", style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)
        self.api_result = ttk.Label(api_frame, text="检测中...", style="Status.TLabel")
        self.api_result.grid(row=0, column=1, sticky=tk.W)
        
        # 实际支持检测
        support_frame = ttk.Frame(result_frame)
        support_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(support_frame, text="实际支持版本:", style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)
        self.support_result = ttk.Label(support_frame, text="检测中...", style="Status.TLabel")
        self.support_result.grid(row=0, column=1, sticky=tk.W)
        
        # 字体检测
        font_frame = ttk.Frame(result_frame)
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(font_frame, text="Segoe UI Emoji 版本:", style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)
        self.font_result = ttk.Label(font_frame, text="检测中...", style="Status.TLabel")
        self.font_result.grid(row=0, column=1, sticky=tk.W)
        
        # 字符测试框架
        test_frame = ttk.LabelFrame(main_frame, text="字符支持测试", padding=10)
        test_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 测试结果表格
        columns = ("version", "char", "status", "name", "release")
        self.tree = ttk.Treeview(test_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.tree.heading("version", text="Unicode 版本")
        self.tree.heading("char", text="字符")
        self.tree.heading("status", text="支持状态")
        self.tree.heading("name", text="名称")
        self.tree.heading("release", text="发布日期")
        
        # 设置列宽
        self.tree.column("version", width=100, anchor=tk.CENTER)
        self.tree.column("char", width=50, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("name", width=150, anchor=tk.W)
        self.tree.column("release", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(test_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        refresh_btn = ttk.Button(button_frame, text="重新检测", command=self.refresh)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="导出报告", command=self.export_report)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.destroy)
        exit_btn.pack(side=tk.RIGHT, padx=5)
    
    def get_system_info(self):
        """获取系统信息"""
        info = {
            "os_name": platform.system(),
            "os_version": platform.release(),
            "build": platform.version(),
            "arch": platform.machine(),
            "python_version": platform.python_version(),
        }
        return info
    
    def get_windows_unicode_version(self):
        """通过Windows API获取精确的Unicode版本（增强兼容性）"""
        os_version = safe_get_windows_version()
        if not os_version:
            return "无法获取系统版本信息"
        
        try:
            # 获取系统信息
            major = os_version.dwMajorVersion
            minor = os_version.dwMinorVersion
            build = os_version.dwBuildNumber
            
            # 映射到Unicode版本
            if major == 10:
                if build >= 22631:  # Win11 23H2
                    return "15.1 (Windows 11 23H2)"
                elif build >= 22621:  # Win11 22H2
                    return "15.0 (Windows 11 22H2)"
                elif build >= 22000:  # Win11 21H2
                    return "14.0 (Windows 11 21H2)"
                elif build >= 19045:  # Win10 22H2
                    return "13.1 (Windows 10 22H2)"
                elif build >= 19044:  # Win10 21H2
                    return "13.0 (Windows 10 21H2)"
                elif build >= 19041:  # Win10 20H2
                    return "12.1 (Windows 10 20H2)"
                else:  # Win10 早期版本
                    return f"12.0 (Windows 10 Build {build})"
            elif major == 6:
                if minor == 3:  # Win8.1
                    return "6.3 (Windows 8.1)"
                elif minor == 2:  # Win8
                    return "6.2 (Windows 8)"
                elif minor == 1:  # Win7
                    return "6.1 (Windows 7)"
                elif minor == 0:  # Vista
                    return "5.0 (Windows Vista)"
            elif major == 5:  # Windows XP
                if minor == 2:  # Windows XP 64位
                    return "4.0 (Windows XP x64)"
                elif minor == 1:  # Windows XP
                    return "3.0 (Windows XP)"
            
            return f"未知 (Windows {major}.{minor} Build {build})"
        except Exception as e:
            return f"API错误: {str(e)}"
        
    def get_segoe_emoji_version(self):
        """增强的字体检测（兼容旧Windows）"""
        font_name = get_segoe_font_name()
        if not font_name:
            return "未找到表情符号字体"
        
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            )
            
            font_file, _ = winreg.QueryValueEx(key, font_name)
            
            # 处理不同字体文件格式
            if "Segoe UI Symbol" in font_name:
                # Windows 8.1 使用此字体
                return "6.3 (Segoe UI Symbol)"
            
            # 构建字体完整路径
            fonts_dir = os.environ.get("SystemRoot", "C:\\Windows") + "\\Fonts\\"
            full_path = os.path.join(fonts_dir, font_file)
            
            if not os.path.exists(full_path):
                # 尝试常见文件名
                possible_files = [
                    "seguiemj.ttf",
                    "seguisym.ttf",
                    "seguihis.ttf",
                    "segmdl2.ttf"
                ]
                for file in possible_files:
                    test_path = os.path.join(fonts_dir, file)
                    if os.path.exists(test_path):
                        full_path = test_path
                        break
            
            if os.path.exists(full_path):
                with open(full_path, "rb") as f:
                    data = f.read(1000)
                
                # 查找版本号
                match = re.search(rb"Version (\d+\.\d+)", data)
                if match:
                    version = match.group(1).decode()
                    # 映射到Unicode版本
                    if version >= "5.00": return f"15.1 (字体版本 {version})"
                    elif version >= "4.00": return f"15.0 (字体版本 {version})"
                    elif version >= "3.00": return f"14.0 (字体版本 {version})"
                    elif version >= "2.00": return f"13.0 (字体版本 {version})"
                    elif version >= "1.00": return f"12.0 (字体版本 {version})"
                
                return "未知版本"
            return "字体文件未找到"
        except Exception as e:
            return f"字体检测错误: {str(e)}"
    
    def test_unicode_support(self):
        """增强的Unicode测试（兼容旧系统）"""
        results = []
        max_supported = "0.0"
        
        # 从高版本到低版本测试
        versions = sorted(UNICODE_TEST_CHARS.keys(), key=float, reverse=True)
        
        for version in versions:
            char_info = UNICODE_TEST_CHARS[version]
            char = char_info["char"]
            name = char_info["name"]
            
            try:
                # 尝试显示字符并检查是否能正确渲染
                test_label = tk.Label(self.root, text=char, font=("Arial", 12))
                test_label.update()
                
                # 获取标签的实际文本内容
                actual_text = test_label.cget("text")

                # 如果实际文本与预期字符不同，则认为不支持
                if actual_text != char or len(actual_text) != len(char):
                    status = f"✗ 不支持"
                    char_name = "N/A"
                else:
                    status = "✓ 支持"
                    try:
                        char_name = unicodedata.name(char, "Unknown")
                    except:
                        char_name = "名称未知"
                    
                    if float(version) > float(max_supported):
                        max_supported = version
                
                test_label.destroy()
            except Exception as e:
                status = f"✗ 不支持"
                char_name = "N/A"
            
            results.append({
                "version": version,
                "char": char,
                "name": name,
                "status": status,
                "char_name": char_name,
                "release_date": UNICODE_TEST_CHARS[version]["version"]
            })
        
        return results, max_supported
    
    def refresh(self):
        """刷新检测结果"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重新检测
        self.detect_unicode_info()

    def export_report(self):
        """导出检测报告"""
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="保存报告"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    # 系统信息
                    f.write("="*60 + "\n")
                    f.write("Unicode 支持检测报告\n".center(60) + "\n")
                    f.write("="*60 + "\n\n")
                    
                    f.write(f"操作系统: {self.os_label.cget('text').split(': ')[1]}\n")
                    f.write(f"构建版本: {self.build_label.cget('text').split(': ')[1]}\n")
                    f.write(f"系统架构: {self.arch_label.cget('text').split(': ')[1]}\n")
                    f.write(f"Python 版本: {self.python_label.cget('text').split(': ')[1]}\n\n")
                    
                    # 检测结果
                    f.write("检测结果:\n")
                    f.write(f"  系统 API 检测: {self.api_result.cget('text')}\n")
                    f.write(f"  实际支持版本: {self.support_result.cget('text')}\n")
                    f.write(f"  Segoe UI Emoji 版本: {self.font_result.cget('text')}\n\n")
                    
                    # 测试结果
                    f.write("字符支持测试:\n")
                    f.write("版本   字符  状态        名称               发布日期\n")
                    f.write("-"*60 + "\n")
                    
                    for item in self.tree.get_children():
                        values = self.tree.item(item, "values")
                        f.write(f"{values[0].ljust(7)} {values[1]}  {values[2].ljust(10)} {values[3].ljust(18)} {values[4]}\n")
                    
                    self.status_var.set(f"报告已导出到: {file_path}")
        except Exception as e:
            self.status_var.set(f"导出失败: {str(e)}")

