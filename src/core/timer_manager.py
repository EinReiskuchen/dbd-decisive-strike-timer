"""
计时器管理模块
"""
import threading
import time
import uuid
import winsound
import os
from . import config

# --- 事件队列 ---
# 该队列将被用于从计时器线程向主GUI线程发送事件
_event_queue = None

def set_event_queue(queue):
    """设置一个队列，用于发送计时器事件。"""
    global _event_queue
    _event_queue = queue

def _put_event(event):
    """向队列中放入一个事件（如果队列已设置）。"""
    if _event_queue:
        _event_queue.put(event)

# --- 计时器实现 ---
class CountdownTimer(threading.Thread):
    """一个独立的、可暂停和取消的倒计时器线程。"""
    def __init__(self, duration):
        super().__init__(daemon=True)
        self.timer_id = str(uuid.uuid4()) # 为每个计时器分配一个唯一ID
        self.duration = duration
        self.remaining = duration
        self._stop_event = threading.Event()

    def run(self):
        """线程主循环，每秒更新一次剩余时间。"""
        _put_event({'type': 'start', 'id': self.timer_id, 'value': self.remaining})

        while self.remaining > 0 and not self._stop_event.is_set():
            time.sleep(1)
            self.remaining -= 1
            _put_event({'type': 'update', 'id': self.timer_id, 'value': self.remaining})

        if not self._stop_event.is_set():
            # 倒计时正常结束
            _put_event({'type': 'finish', 'id': self.timer_id})
            play_sound()
            # 只有正常结束时才发送销毁事件和清理
            _put_event({'type': 'destroy', 'id': self.timer_id})
            _cleanup_timer(self.timer_id)


    def stop(self):
        """停止计时器。"""
        self._stop_event.set()

def _cleanup_timer(timer_id):
    """从管理器中移除一个已完成或已停止的计时器。"""
    with lock:
        if timer_id in timers:
            del timers[timer_id]
            print(f"[{time.strftime('%H:%M:%S')}] 清理完毕，ID: {timer_id}")

# --- 管理器逻辑 ---
timers = {} # 使用字典来存储计时器，key为timer_id
lock = threading.Lock()

def play_sound():
    """播放音效"""
    flags = winsound.SND_PURGE | winsound.SND_ASYNC
    if config.CUSTOM_SOUND_FILE and os.path.isfile(config.CUSTOM_SOUND_FILE):
        winsound.PlaySound(config.CUSTOM_SOUND_FILE, winsound.SND_FILENAME | flags)
    else:
        winsound.PlaySound(config.SYSTEM_SOUND_ALIAS, winsound.SND_ALIAS | flags)

def start_new_timer():
    """启动一个新的计时器。"""
    with lock:
        if len(timers) >= config.MAX_TIMERS:
            print(f"[{time.strftime('%H:%M:%S')}] 计时器已满，无法启动新计时器。")
            return

        new_timer = CountdownTimer(config.TIMEOUT)
        timers[new_timer.timer_id] = new_timer
        new_timer.start()
        print(f"[{time.strftime('%H:%M:%S')}] 启动新计时器，ID: {new_timer.timer_id}")

def clear_all_timers():
    """立即清除所有计时器。"""
    with lock:
        if not timers:
            return

        # 1. 立即向GUI发送清除指令
        _put_event({'type': 'clear_all'})

        # 2. 停止所有计时器线程并清空字典
        count = len(timers)
        for timer in timers.values():
            if timer.is_alive():
                timer.stop()
        timers.clear()

    if count > 0:
        print(f"[{time.strftime('%H:%M:%S')}] 已清空所有计时器，共停止 {count} 个。")

def get_active_timers():
    """获取当前所有活动的计时器"""
    with lock:
        return list(timers.values()) 