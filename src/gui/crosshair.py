"""
准星窗口模块
"""
import tkinter as tk
import sys

class CrosshairWindow(tk.Toplevel):
    """屏幕中央准星窗口"""
    def __init__(self, parent):
        super().__init__(parent)

        # 窗口设置
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.attributes("-alpha", 0.8)

        # 准星大小
        size = 40
        self.geometry(f"{size}x{size}")

        # 居中显示
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - size) // 2
        y = (screen_height - size) // 2
        self.geometry(f"+{x}+{y}")

        # 绘制准星
        canvas = tk.Canvas(self, width=size, height=size, bg="black", highlightthickness=0)
        canvas.pack()

        center = size // 2
        line_length = 12
        thickness = 2
        color = "#00FF00"

        # 绘制十字
        canvas.create_line(center, center - line_length, center, center + line_length,
                          fill=color, width=thickness)
        canvas.create_line(center - line_length, center, center + line_length, center,
                          fill=color, width=thickness)

        # 设置点击穿透（仅Windows）
        if sys.platform == 'win32':
            self.after(100, self._set_click_through)

        self.withdraw()

    def _set_click_through(self):
        """设置窗口为点击穿透（Windows）"""
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style | 0x80000 | 0x20
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        except Exception as e:
            print(f"设置点击穿透失败: {e}")

    def toggle(self):
        """切换显示/隐藏"""
        if self.state() == 'withdrawn':
            self.deiconify()
        else:
            self.withdraw()
