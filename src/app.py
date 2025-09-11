"""
应用入口模块
提供统一的启动接口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import AppManager


def create_app():
    """创建应用实例"""
    return AppManager()


def run_app():
    """运行应用"""
    try:
        app_manager = create_app()
        exit_code = app_manager.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 应用被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_app()