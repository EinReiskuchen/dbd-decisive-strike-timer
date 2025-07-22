"""
输入处理模块
"""

from pynput import keyboard as pk, mouse as pm
from . import config
from . import timer_manager

def on_key_press(key):
    """键盘按下事件的回调函数"""
    # 尝试将按键作为字符处理
    try:
        if config.CLEAR_KEY and key.char == config.CLEAR_KEY:
            timer_manager.clear_all_timers()
            return
        if config.KEY and key.char == config.KEY:
            timer_manager.start_new_timer()
            return
    except AttributeError:
        # 如果不是字符键，则作为特殊键处理
        if config.CLEAR_KEY and key.name == config.CLEAR_KEY:
            timer_manager.clear_all_timers()
            return
        if config.KEY and key.name == config.KEY:
            timer_manager.start_new_timer()
            return

def on_mouse_click(x, y, button, pressed):
    """鼠标点击事件的回调函数"""
    if not pressed:
        return  # 只处理按下事件

    button_name = None
    if button == pm.Button.x1:
        button_name = 'x1'
    elif button == pm.Button.x2:
        button_name = 'x2'

    if config.CLEAR_MOUSE_BUTTON and button_name == config.CLEAR_MOUSE_BUTTON:
        timer_manager.clear_all_timers()
        return

    if config.MOUSE_BUTTON and button_name == config.MOUSE_BUTTON:
        timer_manager.start_new_timer()
        return

def start_listening(stop_event):
    """启动键盘和鼠标的监听器"""
    kl = pk.Listener(on_press=on_key_press)
    ml = pm.Listener(on_click=on_mouse_click)
    kl.daemon = True
    ml.daemon = True
    kl.start()
    ml.start()
    
    print(f"监测 启动计时: 键盘({config.KEY or '无'}), 鼠标({config.MOUSE_BUTTON or '无'})")
    print(f"监测 清空计时: 键盘({config.CLEAR_KEY or '无'}), 鼠标({config.CLEAR_MOUSE_BUTTON or '无'})")
    print(f"最多并发 {config.MAX_TIMERS} 个计时器。按 Ctrl+C 退出。")

    try:
        while not stop_event.is_set():
            stop_event.wait(0.5)
    finally:
        kl.stop()
        ml.stop()
        print("输入监听已停止。") 