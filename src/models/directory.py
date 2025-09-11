from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base

class Directory(Base):
    __tablename__ = "directories"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(500), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    scan_recursive = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    images = relationship("Image", back_populates="directory", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "is_active": self.is_active,
            "scan_recursive": self.scan_recursive,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "image_count": len(self.images)
        }