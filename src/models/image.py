from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), unique=True, nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer, default=0)

    
    # EXIF 信息
    date_taken = Column(DateTime)
    camera_make = Column(String(50))
    camera_model = Column(String(100))
    lens_model = Column(String(100))
    focal_length = Column(Float)
    focal_length_35mm = Column(Float)  # 等效35mm焦距
    aperture = Column(Float)
    shutter_speed = Column(String(20))
    iso = Column(Integer)
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    gps_altitude = Column(Float)
    location = Column(Text)
    orientation = Column(String(50))
    color_space = Column(String(20))
    white_balance = Column(String(20))
    metering_mode = Column(String(20))
    exposure_program = Column(String(20))
    flash = Column(String(20))
    
    # 外键关系
    directory_id = Column(Integer, ForeignKey("directories.id"), nullable=True)
    
    # 关系
    directory = relationship("Directory", back_populates="images")
    albums = relationship("Album", secondary="album_images", back_populates="images")
    thumbnail = relationship("Thumbnail", back_populates="image", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_favorite": self.is_favorite,
            "rating": self.rating,
            "directory_id": self.directory_id,
            "date_taken": self.date_taken.isoformat() if self.date_taken else None,
            "camera_make": self.camera_make,
            "camera_model": self.camera_model,
            "lens_model": self.lens_model,
            "focal_length": self.focal_length,
            "focal_length_35mm": self.focal_length_35mm,
            "aperture": self.aperture,
            "shutter_speed": self.shutter_speed,
            "iso": self.iso,
            "gps_latitude": self.gps_latitude,
            "gps_longitude": self.gps_longitude,
            "gps_altitude": self.gps_altitude,
            "location": self.location,
            "orientation": self.orientation,
            "color_space": self.color_space,
            "white_balance": self.white_balance,
            "metering_mode": self.metering_mode,
            "exposure_program": self.exposure_program,
            "flash": self.flash
        }