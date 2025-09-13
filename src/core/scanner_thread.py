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
from src.models.directory import Directory
import hashlib
import piexif
from datetime import datetime

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
            
            for directory_path in self.directories:
                if not os.path.exists(directory_path):
                    continue
                
                # 获取或创建目录记录
                directory_id = self._get_directory_id(directory_path, Session)
                if not directory_id:
                    continue
                    
                # 扫描目录中的所有图片
                images = self._scan_directory(directory_path)
                total_images += len(images)
                
                # 处理每张图片
                for image_path in images:
                    try:
                        self._process_image(image_path, directory_id, Session)
                        processed_images += 1
                        self.progress_updated.emit(processed_images, total_images)
                    except Exception as e:
                        self.scan_error.emit(f"处理图片失败 {image_path}: {str(e)}")
            
            self.scan_completed.emit(processed_images)
            
        except Exception as e:
            self.scan_error.emit(f"扫描线程错误: {str(e)}")
    
    def _get_directory_id(self, directory_path, Session):
        """获取目录ID，如果不存在则创建"""
        session = Session()
        try:
            # 规范化路径
            normalized_path = os.path.normpath(directory_path)
            
            # 查找现有目录
            directory = session.query(Directory).filter_by(path=normalized_path).first()
            if directory:
                return directory.id
            
            # 创建新目录
            dir_name = os.path.basename(normalized_path)
            new_directory = Directory(
                path=normalized_path,
                name=dir_name
            )
            session.add(new_directory)
            session.commit()
            return new_directory.id
            
        except Exception as e:
            session.rollback()
            print(f"获取目录ID失败: {e}")
            return None
        finally:
            session.close()
    
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
    
    def _process_image(self, image_path, directory_id, Session):
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
            
            # 使用PIL获取基础图片信息
            with PILImage.open(image_path) as img:
                width, height = img.size
                format_name = img.format or file_path.suffix.upper().lstrip('.')
                
                # 创建图片记录（包含EXIF信息）
                image_record = Image(
                    file_path=image_path,
                    file_name=file_path.name,
                    file_size=file_size,
                    width=width,
                    height=height,
                    format=format_name,
                    directory_id=directory_id,
                    **self._extract_exif_data(image_path)
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
            
    def _extract_exif_data(self, image_path):
        """提取EXIF信息"""
        exif_data = {}
        
        try:
            # 尝试读取EXIF数据
            exif_dict = piexif.load(image_path)
            
            # 提取拍摄时间
            if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                exif_data['date_taken'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            elif piexif.ImageIFD.DateTime in exif_dict['0th']:
                date_str = exif_dict['0th'][piexif.ImageIFD.DateTime].decode('utf-8')
                exif_data['date_taken'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            
            # 提取相机信息
            if piexif.ImageIFD.Make in exif_dict['0th']:
                exif_data['camera_make'] = exif_dict['0th'][piexif.ImageIFD.Make].decode('utf-8')
            if piexif.ImageIFD.Model in exif_dict['0th']:
                exif_data['camera_model'] = exif_dict['0th'][piexif.ImageIFD.Model].decode('utf-8')
            
            # 提取镜头信息
            if piexif.ExifIFD.LensModel in exif_dict['Exif']:
                try:
                    exif_data['lens_model'] = exif_dict['Exif'][piexif.ExifIFD.LensModel].decode('utf-8')
                except:
                    exif_data['lens_model'] = str(exif_dict['Exif'][piexif.ExifIFD.LensModel])
            
            # 提取拍摄参数
            if piexif.ExifIFD.FocalLength in exif_dict['Exif']:
                focal_length = exif_dict['Exif'][piexif.ExifIFD.FocalLength]
                exif_data['focal_length'] = float(focal_length[0]) / float(focal_length[1]) if isinstance(focal_length, tuple) else float(focal_length)
                
            if piexif.ExifIFD.FocalLengthIn35mmFilm in exif_dict['Exif']:
                try:
                    exif_data['focal_length_35mm'] = float(exif_dict['Exif'][piexif.ExifIFD.FocalLengthIn35mmFilm])
                except:
                    pass
            
            if piexif.ExifIFD.FNumber in exif_dict['Exif']:
                aperture = exif_dict['Exif'][piexif.ExifIFD.FNumber]
                exif_data['aperture'] = float(aperture[0]) / float(aperture[1]) if isinstance(aperture, tuple) else float(aperture)
            
            if piexif.ExifIFD.ExposureTime in exif_dict['Exif']:
                exposure_time = exif_dict['Exif'][piexif.ExifIFD.ExposureTime]
                if isinstance(exposure_time, tuple):
                    exif_data['shutter_speed'] = f"1/{int(float(exposure_time[1])/float(exposure_time[0]))}"
                else:
                    exif_data['shutter_speed'] = str(exposure_time)
            
            if piexif.ExifIFD.ISOSpeedRatings in exif_dict['Exif']:
                iso = exif_dict['Exif'][piexif.ExifIFD.ISOSpeedRatings]
                exif_data['iso'] = int(iso[0]) if isinstance(iso, tuple) else int(iso)
            
            # 提取GPS信息
            if 'GPS' in exif_dict and exif_dict['GPS']:
                gps_info = exif_dict['GPS']
                if piexif.GPSIFD.GPSLatitude in gps_info and piexif.GPSIFD.GPSLongitude in gps_info:
                    lat = gps_info[piexif.GPSIFD.GPSLatitude]
                    lat_ref = gps_info[piexif.GPSIFD.GPSLatitudeRef]
                    lon = gps_info[piexif.GPSIFD.GPSLongitude]
                    lon_ref = gps_info[piexif.GPSIFD.GPSLongitudeRef]
                    
                    exif_data['gps_latitude'] = self._convert_gps_to_decimal(lat, lat_ref)
                    exif_data['gps_longitude'] = self._convert_gps_to_decimal(lon, lon_ref)
                    
                    if piexif.GPSIFD.GPSAltitude in gps_info:
                        altitude = gps_info[piexif.GPSIFD.GPSAltitude]
                        exif_data['gps_altitude'] = float(altitude[0]) / float(altitude[1]) if isinstance(altitude, tuple) else float(altitude)
            
            # 提取其他信息 - 使用正确的EXIF标签
            if piexif.ImageIFD.Orientation in exif_dict['0th']:
                try:
                    orientation = exif_dict['0th'][piexif.ImageIFD.Orientation]
                    orientation_map = {
                        1: 'Horizontal (normal)', 2: 'Mirror horizontal', 3: 'Rotate 180',
                        4: 'Mirror vertical', 5: 'Mirror horizontal and rotate 270 CW',
                        6: 'Rotate 90 CW', 7: 'Mirror horizontal and rotate 90 CW',
                        8: 'Rotate 270 CW'
                    }
                    exif_data['orientation'] = orientation_map.get(int(orientation), str(int(orientation)))
                except Exception as e:
                    print(f"提取orientation失败: {e}")
                    exif_data['orientation'] = 'Unknown'
            
            # 使用ExifIFD而不是PhotoIFD
            if piexif.ExifIFD.ColorSpace in exif_dict['Exif']:
                try:
                    color_space = exif_dict['Exif'][piexif.ExifIFD.ColorSpace]
                    color_space_map = {1: 'sRGB', 2: 'Adobe RGB', 65535: 'Uncalibrated'}
                    exif_data['color_space'] = color_space_map.get(color_space, str(color_space))
                except Exception as e:
                    print(f"提取color_space失败: {e}")
                    exif_data['color_space'] = 'Unknown'
            
            if piexif.ExifIFD.WhiteBalance in exif_dict['Exif']:
                try:
                    white_balance = exif_dict['Exif'][piexif.ExifIFD.WhiteBalance]
                    white_balance_map = {0: 'Auto', 1: 'Manual', 2: 'Custom', 3: 'One-touch', 4: 'Subtle'}
                    exif_data['white_balance'] = white_balance_map.get(white_balance, str(white_balance))
                except Exception as e:
                    print(f"提取white_balance失败: {e}")
                    exif_data['white_balance'] = 'Unknown'
            
            if piexif.ExifIFD.MeteringMode in exif_dict['Exif']:
                try:
                    metering_mode = exif_dict['Exif'][piexif.ExifIFD.MeteringMode]
                    metering_map = {
                        0: 'Unknown', 1: 'Average', 2: 'Center-weighted average',
                        3: 'Spot', 4: 'Multi-spot', 5: 'Pattern', 6: 'Partial',
                        255: 'Other'
                    }
                    exif_data['metering_mode'] = metering_map.get(metering_mode, str(metering_mode))
                except Exception as e:
                    print(f"提取metering_mode失败: {e}")
                    exif_data['metering_mode'] = 'Unknown'
            
            # 提取曝光程序
            if piexif.ExifIFD.ExposureProgram in exif_dict['Exif']:
                try:
                    exposure_program = exif_dict['Exif'][piexif.ExifIFD.ExposureProgram]
                    exposure_map = {
                        0: 'Not defined', 1: 'Manual', 2: 'Normal program',
                        3: 'Aperture priority', 4: 'Shutter priority', 5: 'Creative program',
                        6: 'Action program', 7: 'Portrait mode', 8: 'Landscape mode'
                    }
                    exif_data['exposure_program'] = exposure_map.get(exposure_program, str(exposure_program))
                except Exception as e:
                    print(f"提取exposure_program失败: {e}")
                    exif_data['exposure_program'] = 'Unknown'
            
            # 提取闪光灯信息
            if piexif.ExifIFD.Flash in exif_dict['Exif']:
                try:
                    flash = exif_dict['Exif'][piexif.ExifIFD.Flash]
                    flash_map = {
                        0: 'No Flash', 1: 'Fired', 5: 'Fired, Return not detected',
                        7: 'Fired, Return detected', 9: 'On', 13: 'On, Return not detected',
                        15: 'On, Return detected', 16: 'Off', 24: 'Auto, Did not fire',
                        25: 'Auto, Fired', 29: 'Auto, Fired, Return not detected',
                        31: 'Auto, Fired, Return detected', 32: 'No flash function',
                        65: 'Fired, Red-eye reduction', 69: 'Fired, Red-eye reduction, Return not detected',
                        71: 'Fired, Red-eye reduction, Return detected', 73: 'On, Red-eye reduction',
                        77: 'On, Red-eye reduction, Return not detected',
                        79: 'On, Red-eye reduction, Return detected', 89: 'Auto, Fired, Red-eye reduction',
                        93: 'Auto, Fired, Red-eye reduction, Return not detected',
                        95: 'Auto, Fired, Red-eye reduction, Return detected'
                    }
                    exif_data['flash'] = flash_map.get(flash, str(flash))
                except Exception as e:
                    print(f"提取flash失败: {e}")
                    exif_data['flash'] = 'Unknown'
            

                
        except Exception as e:
            # EXIF读取失败时返回空字典，使用默认值
            print(f"EXIF提取错误: {e}")
            pass
            
        return exif_data
        
    def _convert_gps_to_decimal(self, gps_coords, ref):
        """将GPS坐标转换为十进制度"""
        try:
            degrees = float(gps_coords[0][0]) / float(gps_coords[0][1])
            minutes = float(gps_coords[1][0]) / float(gps_coords[1][1])
            seconds = float(gps_coords[2][0]) / float(gps_coords[2][1])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref in [b'S', b'W', 'S', 'W']:
                decimal = -decimal
                
            return decimal
        except:
            return None
    
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