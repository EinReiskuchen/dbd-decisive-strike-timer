"""
配置文件
"""

# 启动/重置倒计时的键盘按键，如不监测则设为 None
KEY = None
# 启动/重置倒计时的鼠标侧键：'x1' 或 'x2'，不监测设为 None
MOUSE_BUTTON = 'x1'
# 清空所有待执行计时器的键盘按键，如不监测则设为 None
CLEAR_KEY = None
# 清空所有待执行计时器的鼠标侧键，如不监测则设为 None
CLEAR_MOUSE_BUTTON = 'x2'
# 单个倒计时（秒）
TIMEOUT = 60
# 最大并发计时器数量
MAX_TIMERS = 4
# 系统音效别名
SYSTEM_SOUND_ALIAS = 'SystemExclamation'
# 自定义音效（wav 文件路径），无则设为 None
CUSTOM_SOUND_FILE = None
# 是否将窗口始终置顶
WINDOW_TOPMOST = True 