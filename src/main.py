import threading
import queue
import signal
from .core import timer_manager, input_handler
from .gui import main_window, tray_icon

def main():
    """
    主函数，应用程序的入口点。
    """
    stop_event = threading.Event()
    event_queue = queue.Queue()
    tray_icon_instance = [None] 

    timer_manager.set_event_queue(event_queue)
    app = main_window.App(event_queue)

    # --- 统一的关闭流程 ---
    def on_close_request():
        """当收到退出请求时，安全地启动关闭流程。"""
        print("开始关闭流程...")
        app.quit() # 停止mainloop，让程序继续向下执行

    app.close_app = on_close_request
    app.protocol("WM_DELETE_WINDOW", app.withdraw)

    # --- 统一的信号/事件处理 ---
    def sigint_handler(sig, frame):
        """捕获Ctrl+C信号，并将其转换为一个安全的'exit'事件。"""
        print("\n捕获到 Ctrl+C, 发送退出事件...")
        event_queue.put({'type': 'exit'})

    signal.signal(signal.SIGINT, sigint_handler)

    # --- 启动后台线程 ---
    tray_thread = threading.Thread(
        target=lambda: tray_icon.setup_tray_icon(app, tray_icon_instance, event_queue),
        daemon=True
    )
    tray_thread.start()

    print("欢迎使用 Strike Timer！")

    listener_thread = threading.Thread(
        target=input_handler.start_listening, 
        args=(stop_event,),
        daemon=True
    )
    listener_thread.start()

    app.mainloop()
    
    # --- MAINLOOP 已结束, 现在按顺序清理所有资源 ---
    print("GUI主循环已结束, 正在清理...")
    
    if tray_icon_instance[0]:
        tray_icon_instance[0].stop()
    stop_event.set()
    
    listener_thread.join(timeout=1)
    tray_thread.join(timeout=1)
    
    timer_manager.clear_all_timers()
    app.destroy()
    print("已退出。所有资源已清理。")

if __name__ == '__main__':
    main()
