"""
数据库初始化模块
负责创建数据库和表结构
"""

import os
import logging
from pathlib import Path
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from src.core.database import engine, Base
from src.models import Directory, Image, Album, Thumbnail

logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器"""
    
    @staticmethod
    def initialize_database():
        """
        初始化数据库
        如果数据库文件不存在则创建
        创建所有表结构
        """
        try:
            # 确保数据目录存在
            data_dir = Path("./data")
            data_dir.mkdir(exist_ok=True)
            
            # 检查数据库文件是否存在
            db_file = data_dir / "image_manager.db"
            db_exists = db_file.exists()
            
            if not db_exists:
                logger.info("数据库文件不存在，正在创建...")
            else:
                logger.info("数据库文件已存在，检查表结构...")
            
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            
            # 验证表是否创建成功
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['directories', 'images', 'albums', 'album_images', 'thumbnails']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"缺少表: {missing_tables}")
                return False
            
            logger.info(f"数据库初始化完成，包含表: {tables}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"数据库初始化失败: {e}")
            return False
        except Exception as e:
            logger.error(f"数据库初始化时发生未知错误: {e}")
            return False
    
    @staticmethod
    def check_database_health():
        """
        检查数据库健康状态
        返回数据库状态和表信息
        """
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            health_info = {
                "database_exists": Path("./data/image_manager.db").exists(),
                "tables_count": len(tables),
                "tables": tables,
                "healthy": len(tables) > 0
            }
            
            return health_info
            
        except Exception as e:
            logger.error(f"检查数据库健康状态时出错: {e}")
            return {
                "database_exists": False,
                "tables_count": 0,
                "tables": [],
                "healthy": False,
                "error": str(e)
            }
    
    @staticmethod
    def reset_database():
        """
        重置数据库
        删除所有表并重新创建
        谨慎使用！
        """
        try:
            logger.warning("正在重置数据库，所有数据将被删除...")
            
            # 删除所有表
            Base.metadata.drop_all(bind=engine)
            
            # 重新创建所有表
            Base.metadata.create_all(bind=engine)
            
            logger.info("数据库重置完成")
            return True
            
        except Exception as e:
            logger.error(f"重置数据库失败: {e}")
            return False

# 初始化函数
def init_database():
    """快捷初始化函数"""
    return DatabaseInitializer.initialize_database()

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初始化数据库
    success = init_database()
    if success:
        print("✅ 数据库初始化成功")
        
        # 检查健康状态
        health = DatabaseInitializer.check_database_health()
        print(f"数据库状态: {health}")
    else:
        print("❌ 数据库初始化失败")