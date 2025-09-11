from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "sqlite:///./data/image_manager.db"

# 创建引擎
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_size=20,  # 连接池大小
    max_overflow=30,  # 最大溢出连接数
    pool_timeout=60,  # 连接超时时间（秒）
    pool_recycle=3600  # 连接回收时间（秒）
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()