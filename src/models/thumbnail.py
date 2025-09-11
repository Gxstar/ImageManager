from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base

class Thumbnail(Base):
    __tablename__ = "thumbnails"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=True, index=True)
    thumbnail_path = Column(String(500), nullable=False)  # 缩略图文件路径
    width = Column(Integer, default=150)  # 缩略图宽度
    height = Column(Integer, default=150)  # 缩略图高度
    file_size = Column(Integer)  # 文件大小(字节)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    image = relationship("Image", back_populates="thumbnail")
    
    def to_dict(self):
        return {
            "id": self.id,
            "image_id": self.image_id,
            "thumbnail_path": self.thumbnail_path,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }