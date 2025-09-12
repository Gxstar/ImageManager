"""
图片扫描线程模块
"""
import os
import threading
from pathlib import Path
from PIL import Image as PILImage
from PySide6.QtCore import QObject, Signal, QThread
from sqlalchemy.orm import sessionmaker
from src.core.database import engine
from src.models.image import Image
from src.models.thumbnail import Thumbnail
import hashlib

class ImageScannerThread(QThread):
    """后台图片扫描线程"""
    
    progress_updated = Signal(int, int)  # 当前进度, 总数
    scan_completed = Signal(int)  # 扫描完成的图片数量
    scan_error = Signal(str)  # 扫描错误信息
    
    def __init__(self, directories):
        super().__init__()
        self.directories = directories
        self.thumbnail_dir = Path("thumbnails")
        self.thumbnail_dir.mkdir(exist_ok=True)
        
        # 支持的图片格式
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                                '.tiff', '.tif', '.webp', '.ico', '.heic', '.heif'}
        
    def run(self):
        """线程运行入口"""
        try:
            total_images = 0
            processed_images = 0
            
            # 创建数据库会话
            Session = sessionmaker(bind=engine)
            
            for directory in self.directories:
                if not os.path.exists(directory):
                    continue
                    
                # 扫描目录中的所有图片
                images = self._scan_directory(directory)
                total_images += len(images)
                
                # 处理每张图片
                for image_path in images:
                    try:
                        self._process_image(image_path, Session)
                        processed_images += 1
                        self.progress_updated.emit(processed_images, total_images)
                    except Exception as e:
                        self.scan_error.emit(f"处理图片失败 {image_path}: {str(e)}")
            
            self.scan_completed.emit(processed_images)
            
        except Exception as e:
            self.scan_error.emit(f"扫描线程错误: {str(e)}")
    
    def _scan_directory(self, directory):
        """扫描目录中的图片文件"""
        images = []
        for root, dirs, files in os.walk(directory):
            # 忽略隐藏文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.supported_formats:
                        images.append(str(file_path))
        return images
    
    def _process_image(self, image_path, Session):
        """处理单张图片"""
        session = Session()
        try:
            # 检查图片是否已存在
            existing_image = session.query(Image).filter_by(file_path=image_path).first()
            if existing_image:
                return
            
            # 获取图片信息
            file_path = Path(image_path)
            file_size = file_path.stat().st_size
            
            # 使用PIL获取图片信息
            with PILImage.open(image_path) as img:
                width, height = img.size
                format_name = img.format or file_path.suffix.upper().lstrip('.')
                
                # 创建图片记录
                image_record = Image(
                    file_path=image_path,
                    file_name=file_path.name,
                    file_size=file_size,
                    width=width,
                    height=height,
                    format=format_name
                )
                
                session.add(image_record)
                session.flush()  # 获取ID
                
                # 生成缩略图
                thumbnail_path = self._create_thumbnail(image_path, image_record.id)
                
                # 创建缩略图记录
                thumbnail_record = Thumbnail(
                    image_id=image_record.id,
                    thumbnail_path=thumbnail_path,
                    width=150,
                    height=150
                )
                
                session.add(thumbnail_record)
                session.commit()
                
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _create_thumbnail(self, image_path, image_id):
        """创建缩略图"""
        try:
            # 生成缩略图文件名
            file_hash = hashlib.md5(str(image_path).encode()).hexdigest()
            thumbnail_filename = f"{image_id}_{file_hash}.jpg"
            thumbnail_path = self.thumbnail_dir / thumbnail_filename
            
            # 如果缩略图已存在，直接返回路径
            if thumbnail_path.exists():
                return str(thumbnail_path)
            
            # 创建缩略图
            with PILImage.open(image_path) as img:
                # 转换为RGB模式（处理RGBA等模式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算缩略图尺寸（保持宽高比）
                img.thumbnail((150, 150), PILImage.Resampling.LANCZOS)
                
                # 保存缩略图
                img.save(thumbnail_path, 'JPEG', quality=85)
                
            return str(thumbnail_path)
            
        except Exception as e:
            raise Exception(f"创建缩略图失败: {str(e)}")