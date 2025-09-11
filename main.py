#!/usr/bin/env python3
"""
图片管理器 - 入口文件
这是一个纯粹的入口文件，只负责启动应用
"""

import sys
import os
from pathlib import Path

# 确保项目根目录在Python路径中
if __name__ == "__main__":
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 导入并运行应用
    try:
        from src.app import run_app
        run_app()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保项目结构正确")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)
