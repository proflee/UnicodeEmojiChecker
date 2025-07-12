import tkinter as tk
from gui import UnicodeCheckerApp
from utils import check_python_compatibility
from tkinter import messagebox

if __name__ == "__main__":
    if not check_python_compatibility():
        exit(1)

    root = tk.Tk()
    try:
        app = UnicodeCheckerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"应用程序启动失败: {str(e)}")