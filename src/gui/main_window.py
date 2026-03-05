"""
GUI主窗口模块
"""
import tkinter as tk
from ..core import config

class App(tk.Tk):
    """主应用程序窗口"""
    def __init__(self, event_queue):
        super().__init__()
        self.event_queue = event_queue
        
        # --- 恢复为更简单的列表来管理控件 ---
        self.timer_widgets = {}     # {timer_id: Label_widget}

        # --- 窗口基础设置 ---
        self.title("Strike Timer")
        self.overrideredirect(True)
        self.attributes("-alpha", 0.9)
        if config.WINDOW_TOPMOST:
            self.attributes("-topmost", True)
        
        self.main_frame = tk.Frame(self, bg="#333333")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 窗口拖动所需变量 ---
        self._offset_x = 0
        self._offset_y = 0

        # --- 创建UI、绑定事件、启动循环 ---
        self._create_widgets()
        self.update_window_size()
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.process_queue()

    def _create_widgets(self):
        """创建基础UI组件，如待机标签。"""
        self.standby_label = tk.Label(
            self.main_frame, text="空闲",
            font=("黑体", 16),
            fg="#888888", bg="#333333"
        )
        self.standby_label.pack(pady=10, padx=10, fill=tk.X)
            
    def process_queue(self):
        """周期性地处理事件队列中的事件。"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                self.handle_event(event)
        finally:
            self.after(100, self.process_queue)

    def handle_event(self, event):
        """根据事件类型处理UI更新。"""
        event_type = event['type']
        
        # 优先处理不需要'id'的事件
        if event_type == 'clear_all':
            self.clear_all_widgets()
            return
        
        if event_type == 'exit':
            self.close_app()
            return

        timer_id = event.get('id')
        if not timer_id: return

        if event_type == 'start':
            if self.standby_label.winfo_ismapped():
                self.standby_label.pack_forget()
            
            new_label = tk.Label(self.main_frame, font=("Segoe UI", 22, "bold"), width=4)
            new_label.pack(pady=5, padx=10, fill=tk.X)
            self.timer_widgets[timer_id] = new_label
            self.update_timer_display(timer_id, event['value'])

        elif event_type in ['update', 'finish']:
            self.update_timer_display(timer_id, event.get('value', 0))

        elif event_type == 'destroy':
            widget = self.timer_widgets.pop(timer_id, None)
            if widget:
                widget.destroy()

        # 统一检查UI状态
        if not self.timer_widgets and not self.standby_label.winfo_ismapped():
            self.standby_label.pack(pady=10, padx=10, fill=tk.X)
        
        self.update_window_size()

    def clear_all_widgets(self):
        """立即销毁所有计时器控件。"""
        for widget in self.timer_widgets.values():
            widget.destroy()
        self.timer_widgets.clear()

    def update_window_size(self):
        """根据计时器数量动态调整窗口大小。"""
        num_timers = len(self.timer_widgets)
        if num_timers == 0:
            height = 50
            width = 120
        else:
            height = num_timers * 55 # 每个计时器大约55像素高
            width = 120
        self.geometry(f"{width}x{height}")

    def update_timer_display(self, timer_id, remaining):
        """更新指定计时器标签的显示内容和样式。"""
        label = self.timer_widgets.get(timer_id)
        if not label: return
        
        if remaining is None:
            text, fg, bg = " -- ", "#FFFFFF", "#555555"
        elif remaining == 0:
            text, fg, bg = "Done!", "#000000", "#FFFFFF"
        else:
            text, fg, bg = f"{remaining:02d}", "#FFFFFF", "#555555"

        label.config(text=text, fg=fg, bg=bg)

    def _on_click(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _on_drag(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def close_app(self, event=None):
        """这个方法将在main.py中被重新指向真正的关闭逻辑。"""
        pass

if __name__ == '__main__':
    import queue
    q = queue.Queue()
    app = App(q)
    
    def test_events():
        q.put({'type': 'start', 'id': 'timer1', 'value': 60})
        app.after(1000, lambda: q.put({'type': 'update', 'id': 'timer1', 'value': 59}))
        app.after(2000, lambda: q.put({'type': 'start', 'id': 'timer2', 'value': 60}))
        app.after(3000, lambda: q.put({'type': 'start', 'id': 'timer3', 'value': 60}))
        app.after(4000, lambda: q.put({'type': 'destroy', 'id': 'timer1'}))
        app.after(5000, lambda: q.put({'type': 'destroy', 'id': 'timer2'}))
        app.after(6000, lambda: q.put({'type': 'clear_all'}))

    app.after(500, test_events)
    app.mainloop() 