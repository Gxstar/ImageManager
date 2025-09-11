from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base

# 关联表：相册和图片的多对多关系
album_images = Table(
    'album_images',
    Base.metadata,
    Column('album_id', Integer, ForeignKey('albums.id'), primary_key=True),
    Column('image_id', Integer, ForeignKey('images.id'), primary_key=True),
    Column('sort_order', Integer, default=0),
    Column('added_at', DateTime, default=datetime.now)
)

class Album(Base):
    __tablename__ = "albums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    cover_image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    images = relationship("Image", secondary=album_images, back_populates="albums")
    cover_image = relationship("Image")
    
    def to_dict(self, include_stats=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cover_image_id": self.cover_image_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_stats:
            data["image_count"] = len(self.images)
            
        return data