"""
系统托盘图标模块
"""
from PIL import Image, ImageDraw, ImageFont
import pystray
import os

ICO_PATH = "resources/icon.ico"
PNG_SOURCE_PATH = "resources/icon.png"

def ensure_icon_exists():
    """
    确保托盘图标文件存在。
    优先级: icon.ico > icon.png > 动态生成。
    """
    if os.path.exists(ICO_PATH):
        return

    # --- 如果ICO不存在, 尝试从PNG源文件创建 ---
    if os.path.exists(PNG_SOURCE_PATH):
        try:
            print(f"从 {PNG_SOURCE_PATH} 创建ICO文件...")
            source_image = Image.open(PNG_SOURCE_PATH)
            # 为了最好的兼容性，提供多个尺寸
            sizes = [(16,16), (24,24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            source_image.save(ICO_PATH, format="ICO", sizes=sizes)
            print(f"图标已创建于: {ICO_PATH}")
            return
        except Exception as e:
            print(f"从PNG创建ICO失败: {e}")

    # --- 如果以上都失败, 则动态生成一个备用图标 ---
    print("未找到有效图标源, 生成备用图标...")
    width, height = 64, 64
    bg_color = "#333333"
    fg_color = "#FFFFFF"
    
    image = Image.new('RGB', (width, height), bg_color)
    dc = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("segoeui.ttf", 48)
    except IOError:
        font = ImageFont.load_default()

    dc.text((width/2, height/2), "S", font=font, fill=fg_color, anchor="mm")
    
    os.makedirs(os.path.dirname(ICO_PATH), exist_ok=True)
    image.save(ICO_PATH, format="ICO")
    print(f"备用图标已创建于: {ICO_PATH}")

def setup_tray_icon(app, icon_instance_ref, event_queue):
    """
    设置并运行系统托盘图标。
    这个函数会阻塞，所以应该在一个独立的线程中运行。
    """
    ensure_icon_exists()
    icon_image = Image.open(ICO_PATH)
    
    def on_clicked(icon, item):
        """定义菜单项被点击时的行为"""
        if str(item) == "显示/隐藏":
            if app.state() == 'withdrawn':
                app.deiconify() # 显示窗口
            else:
                app.withdraw() # 隐藏窗口
        elif str(item) == "退出":
            event_queue.put({'type': 'exit'}) # 发送退出事件
            icon.stop() # 停止托盘线程

    # 创建菜单项
    menu = (
        pystray.MenuItem('显示/隐藏', on_clicked, default=True),
        pystray.MenuItem('退出', on_clicked)
    )

    # 创建并运行托盘图标
    icon = pystray.Icon("StrikeTimer", icon_image, "Strike Timer", menu)
    icon_instance_ref[0] = icon # 将icon实例存入引用列表
    icon.run() 