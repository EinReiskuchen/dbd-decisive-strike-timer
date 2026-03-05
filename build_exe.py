"""
打包脚本 - 将项目打包成 .exe 文件
运行此脚本会自动调用 PyInstaller 打包应用程序
"""
import os
import subprocess
import sys

def build():
    """执行打包流程"""
    print("=" * 60)
    print("开始打包 Strike Timer")
    print("=" * 60)

    # 根据平台选择路径分隔符
    separator = ';' if sys.platform == 'win32' else ':'

    # PyInstaller 命令参数
    cmd = [
        'pyinstaller',
        '--name=StrikeTimer',           # 生成的exe名称
        '--onefile',                     # 打包成单个exe文件
        '--windowed',                    # 不显示控制台窗口（GUI应用）
        '--icon=resources/icon.ico',     # 图标文件（如果存在）
        f'--add-data=resources{separator}resources', # 包含resources目录
        '--clean',                       # 清理临时文件
        'run.py'                         # 入口脚本
    ]
    
    # 检查图标文件是否存在
    if not os.path.exists('resources/icon.ico'):
        print("⚠️  警告: 未找到 resources/icon.ico，将使用默认图标")
        # 移除 --icon 参数
        cmd = [c for c in cmd if not c.startswith('--icon=')]
    
    print(f"\n执行命令: {' '.join(cmd)}\n")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("✅ 打包完成!")
        print("=" * 60)
        print(f"\n生成的文件位于: dist\\StrikeTimer.exe")
        print("\n你可以直接运行 dist\\StrikeTimer.exe 来启动应用程序")
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("❌ 打包失败!")
        print("=" * 60)
        print(f"\n错误信息: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n" + "=" * 60)
        print("❌ 未找到 PyInstaller!")
        print("=" * 60)
        print("\n请先安装 PyInstaller:")
        print("  pip install pyinstaller")
        sys.exit(1)

if __name__ == '__main__':
    # 确保在项目根目录运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    build()
