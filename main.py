# 修改QApplication.exec_()为exec()以消除弃用警告
from PySide6.QtWidgets import QApplication
from gui import UnicodeCheckerWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnicodeCheckerWindow()
    window.show()
    sys.exit(app.exec())  # 从exec_()改为exec()