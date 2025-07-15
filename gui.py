# 新建文件 gui_pyqt.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTableView, 
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QScrollArea, QComboBox, 
    QStatusBar, QFileDialog, QPlainTextEdit
)
import sys
from utils import get_system_info, get_windows_unicode_version, get_segoe_emoji_version, get_segoe_font_name,check_python_compatibility
from config import UNICODE_TEST_CHARS
import unicodedata

class UnicodeCheckerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unicode 版本检测工具")
        self.resize(800, 600)
        
        # 主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建界面组件
        self.create_widgets()
        
        # 检测Unicode信息
        self.detect_unicode_info()

    def detect_unicode_info(self):
        self.status_bar.showMessage("正在检测系统信息...")
        
        # 获取系统信息
        sys_info = get_system_info()
        self.os_label.setText(f"操作系统: {sys_info['os_name']} {sys_info['os_version']}")
        self.build_label.setText(f"构建版本: {sys_info['build']}")
        self.arch_label.setText(f"系统架构: {sys_info['arch']}")
        self.python_label.setText(f"Python 版本: {sys_info['python_version']}")

        # 新增：Python兼容性检查
        is_compatible, comp_msg = check_python_compatibility()
        self.compat_result.setText(f"Python 兼容性: {'✓ 兼容' if is_compatible else '✗ 不兼容'} - {comp_msg}")

        # 获取API检测结果
        self.status_bar.showMessage("正在通过系统API检测Unicode版本...")
        api_result = self.get_windows_unicode_version()
        self.api_result.setText(f"系统 API 检测: {api_result}")

        # 获取字体检测结果
        self.status_bar.showMessage("正在检测Segoe UI Emoji字体版本...")
        font_result = get_segoe_emoji_version()
        self.font_result.setText(f"Segoe UI Emoji 版本: {font_result}")

        # 新增：实际支持版本检测逻辑
        actual_version = self.determine_actual_unicode_support(api_result, font_result)
        self.support_result.setText(f"实际支持版本: {actual_version}")

        # 调用 test_unicode_support 并将结果显示到表格中
        test_results, _ = self.test_unicode_support()
        for result in test_results:
            self.table_model.appendRow([
                QStandardItem(result["version"]),
                QStandardItem(result["char"]),
                QStandardItem(result["status"]),
                QStandardItem(result["name"]),
                QStandardItem(result["release_date"])
            ])

    def create_widgets(self):
        # 检测结果框架
        result_frame = QFrame()
        result_layout = QVBoxLayout()
        
        # 系统信息标签（新增以下4行）
        self.os_label = QLabel("操作系统: 检测中...")
        result_layout.addWidget(self.os_label)
        self.build_label = QLabel("构建版本: 检测中...")
        result_layout.addWidget(self.build_label)
        self.arch_label = QLabel("系统架构: 检测中...")
        result_layout.addWidget(self.arch_label)
        self.python_label = QLabel("Python 版本: 检测中...")
        result_layout.addWidget(self.python_label)

        # API检测结果
        self.api_result = QLabel("系统 API 检测: 检测中...")
        result_layout.addWidget(self.api_result)
        
        # 新增：Python兼容性检测结果标签
        self.compat_result = QLabel("Python 兼容性: 检测中...")
        result_layout.addWidget(self.compat_result)
        
        # 新增：字体检测结果标签（修复缺失的初始化）
        self.font_result = QLabel("Segoe UI Emoji 版本: 检测中...")
        result_layout.addWidget(self.font_result)
        
        # 实际支持检测
        self.support_result = QLabel("实际支持版本: 检测中...")
        result_layout.addWidget(self.support_result)

        result_frame.setLayout(result_layout)
        self.layout.addWidget(result_frame)

        # 字符测试框架
        test_frame = QFrame()
        test_layout = QVBoxLayout()
        
        # 表格视图
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["Unicode 版本", "字符", "支持状态", "名称", "发布日期"])
        
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        test_layout.addWidget(self.table_view)
        test_frame.setLayout(test_layout)
        self.layout.addWidget(test_frame)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 按钮框架
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("重新检测")
        refresh_btn.clicked.connect(self.refresh)
        
        export_btn = QPushButton("导出报告")
        export_btn.clicked.connect(self.export_report)
        
        exit_btn = QPushButton("退出")
        exit_btn.clicked.connect(self.close)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(exit_btn)
        button_frame.setLayout(button_layout)
        self.layout.addWidget(button_frame)

    def determine_actual_unicode_support(self, api_version, font_version):
        """根据API检测结果和字体版本确定实际支持的Unicode版本"""
        try:
            # 解析API版本号
            api_major = int(api_version.split('.')[0])
            
            # 根据字体版本确定最大支持版本
            if font_version.startswith("5.00"):
                return "15.1" if api_major >= 15 else "14.0"
            elif font_version.startswith("3.00"):
                return "14.0" if api_major >= 14 else "12.1"
            elif font_version.startswith("1.51"):
                return "12.1" if api_major >= 12 else "12.0"
            else:
                return "12.0"
        except Exception as e:
            print(f"确定实际支持版本失败: {str(e)}")
            return "检测失败"

    def get_windows_unicode_version(self):
        """
        获取系统API检测到的Unicode版本
        调用工具函数实现具体检测逻辑
        """
        return get_windows_unicode_version()

    def test_unicode_support(self):
        results = []
        max_supported = "0.0"
        
        # 获取系统支持的Emoji字体名称
        segoe_font = get_segoe_font_name() or "Segoe UI Emoji"
        # 提取基础字体名称（去掉后面可能的(TrueType)标识）
        font_family = segoe_font.split(" (")[0] if " " in segoe_font else segoe_font
    
        # 创建测试标签
        test_label = QLabel()
        
        # 从高版本到低版本测试
        versions = sorted(UNICODE_TEST_CHARS.keys(), key=float, reverse=True)
        
        for version in versions:
            char_info = UNICODE_TEST_CHARS[version]
            char = char_info["char"]
            name = char_info["name"]
            
            try:
                # 使用准确的字体名称并增加字号以更好显示彩色Emoji
                test_font = QFont(font_family, 16)
                test_label.setFont(test_font)
                test_label.setText(char)
                
                # 获取标签的实际文本内容
                actual_text = test_label.text()

                # 如果实际文本与预期字符不同，则认为不支持
                if actual_text != char or len(actual_text) != len(char):
                    status = "✗ 不支持"
                    print(f"{version}: 不支持")
                else:
                    status = "✓ 支持"                    
                    if float(version) > float(max_supported):
                        max_supported = version
            except Exception as e:
                status = "✗ 不支持"
                print(f"{version}: 检测失败: {str(e)}")
            
            results.append({
                "version": version,
                "char": char,
                "name": name,
                "status": status,
                "release_date": UNICODE_TEST_CHARS[version]["version"]
            })
        
        return results, max_supported

    def refresh(self):
        """刷新检测结果"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        self.detect_unicode_info()

    def export_report(self):
        """导出检测报告"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存报告",
                "",
                "文本文件 (*.txt);;所有文件 (*)"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    # 系统信息
                    f.write("="*60 + "\n")
                    f.write("Unicode 支持检测报告\n".center(60) + "\n")
                    f.write("="*60 + "\n\n")
                    
                    f.write(f"操作系统: {self.os_label.text().split(': ')[1]}\n")
                    f.write(f"构建版本: {self.build_label.text().split(': ')[1]}\n")
                    f.write(f"系统架构: {self.arch_label.text().split(': ')[1]}\n")
                    f.write(f"Python 版本: {self.python_label.text().split(': ')[1]}\n\n")
                    
                    # 检测结果
                    f.write("检测结果:\n")
                    f.write(f"  系统 API 检测: {self.api_result.text().split(': ')[1]}\n")
                    f.write(f"  实际支持版本: {self.support_result.text().split(': ')[1]}\n")
                    f.write(f"  Segoe UI Emoji 版本: {self.font_result.text().split(': ')[1]}\n\n")
                    
                    # 测试结果
                    f.write("字符支持测试:\n")
                    f.write("版本   字符  状态        名称               发布日期\n")
                    f.write("-"*60 + "\n")
                    
                    for row in range(self.table_model.rowCount()):
                        version = self.table_model.item(row, 0).text()
                        char = self.table_model.item(row, 1).text()
                        status = self.table_model.item(row, 2).text()
                        name = self.table_model.item(row, 3).text()
                        release = self.table_model.item(row, 4).text()
                        
                        f.write(f"{version.ljust(7)} {char}  {status.ljust(10)} {name.ljust(18)} {release}\n")
                    
                self.status_bar.showMessage(f"报告已导出到: {file_path}")
        except Exception as e:
            self.status_bar.showMessage(f"导出失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnicodeCheckerWindow()
    window.show()
    sys.exit(app.exec_())

