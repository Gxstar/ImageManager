"""
主窗口类 - 简洁版本
负责应用的主界面和交互逻辑
"""

import sys
import os
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                              QMessageBox, QTreeWidgetItem, QMenu, QProgressBar, QLabel,
                              QListView, QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import (QPixmap, QImage, QPainter, QFont, QFontDatabase,
                           QStandardItemModel, QStandardItem, QKeySequence, QTransform,
                           QShortcut)
import PySide6.QtGui as QtGui
from src.core.scanner_thread import ImageScannerThread
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
import qtawesome as qta

from src.core.initializer import DatabaseInitializer
from src.core.database import get_db
from src.models.directory import Directory
from src.models.image import Image
from src.models.thumbnail import Thumbnail

from PySide6.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox, 
                              QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                              QDialog, QListWidgetItem, QTreeWidgetItem, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal, QDir, QTimer, QSettings, QSize, QUrl, QEvent
from PySide6.QtGui import QPixmap, QImage, QIcon, QFont, QShortcut, QTransform, QImageReader, QImageIOHandler


class ImagePreviewWindow(QDialog):
    """图片预览窗口"""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = None
        self.current_scale = 1.0
        self.rotation_angle = 0  # 旋转角度
        
        self.setWindowTitle("图片预览")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_image()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        # 图片显示区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(100, 100)
        self.image_label.setScaledContents(False)  # 禁用自动缩放，我们手动控制
        
        # 启用鼠标追踪以支持滚轮事件
        self.image_label.setMouseTracking(True)
        scroll_area.setMouseTracking(True)
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # 控制按钮
        controls_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("放大")
        zoom_in_btn.clicked.connect(self.zoom_in)
        controls_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("缩小")
        zoom_out_btn.clicked.connect(self.zoom_out)
        controls_layout.addWidget(zoom_out_btn)
        
        fit_btn = QPushButton("适应窗口")
        fit_btn.clicked.connect(self.fit_to_window)
        controls_layout.addWidget(fit_btn)
        
        original_btn = QPushButton("原始大小")
        original_btn.clicked.connect(self.original_size)
        controls_layout.addWidget(original_btn)
        
        rotate_left_btn = QPushButton("向左旋转")
        rotate_left_btn.clicked.connect(lambda: self.rotate_image(-90))
        controls_layout.addWidget(rotate_left_btn)
        
        rotate_right_btn = QPushButton("向右旋转")
        rotate_right_btn.clicked.connect(lambda: self.rotate_image(90))
        controls_layout.addWidget(rotate_right_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # 快捷键
        QShortcut(Qt.Key_Plus, self, self.zoom_in)
        QShortcut(Qt.Key_Minus, self, self.zoom_out)
        QShortcut(Qt.Key_0, self, self.fit_to_window)
        QShortcut(Qt.Key_1, self, self.original_size)
        QShortcut(Qt.Key_Left, self, lambda: self.rotate_image(-90))
        QShortcut(Qt.Key_Right, self, lambda: self.rotate_image(90))
        QShortcut(Qt.Key_Escape, self, self.close)
        
        # 设置滚轮事件过滤器
        scroll_area.installEventFilter(self)
        self.image_label.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """事件过滤器，处理鼠标滚轮事件"""
        if event.type() == QEvent.Wheel:
            # 检查是否有Ctrl键按下，如果没有则进行缩放
            if event.modifiers() & Qt.ControlModifier:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
                return True
            else:
                # 没有Ctrl键时，正常滚动
                return super().eventFilter(obj, event)
        return super().eventFilter(obj, event)
        
    def load_image(self):
        """加载图片"""
        try:
            if os.path.exists(self.image_path):
                # 使用QImage加载图片以获取EXIF信息
                image = QImage(self.image_path)
                if not image.isNull():
                    # 获取并应用正确的旋转方向
                    self.apply_rotation_from_exif(image)
                    self.original_pixmap = QPixmap.fromImage(image)
                    if not self.original_pixmap.isNull():
                        # 默认适应窗口大小
                        self.fit_to_window()
                    else:
                        QMessageBox.warning(self, "错误", "无法加载图片")
                else:
                    QMessageBox.warning(self, "错误", "无法加载图片")
            else:
                QMessageBox.warning(self, "错误", "图片文件不存在")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图片失败: {str(e)}")
            
    def apply_rotation_from_exif(self, image):
        """根据EXIF信息应用正确的旋转方向"""
        try:
            # 使用QImageReader读取EXIF信息
            from PySide6.QtGui import QImageReader
            
            reader = QImageReader(self.image_path)
            if reader.canRead():
                # 获取图片的变换信息（包括旋转）
                transform = reader.transformation()
                
                # 根据变换类型应用旋转
                if transform == QImageIOHandler.TransformationRotate90:
                    self.rotation_angle = 90
                elif transform == QImageIOHandler.TransformationRotate180:
                    self.rotation_angle = 180
                elif transform == QImageIOHandler.TransformationRotate270:
                    self.rotation_angle = 270
                else:
                    self.rotation_angle = 0
                    
                # 应用旋转到QImage
                if self.rotation_angle != 0:
                    transform_matrix = QTransform()
                    transform_matrix.rotate(self.rotation_angle)
                    image = image.transformed(transform_matrix, Qt.SmoothTransformation)
                    
        except Exception as e:
            print(f"应用旋转时出错: {e}")
            self.rotation_angle = 0
            
    def wheelEvent(self, event):
        """处理鼠标滚轮事件"""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
            
    def zoom_in(self):
        """放大"""
        self.current_scale *= 1.2
        self.update_image_display()
        
    def zoom_out(self):
        """缩小"""
        self.current_scale = max(0.1, self.current_scale / 1.2)  # 防止缩放太小
        self.update_image_display()
        
    def fit_to_window(self):
        """适应窗口"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # 获取可用的显示区域大小（考虑滚动条）
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                viewport_size = scroll_area.viewport().size()
                pixmap_size = self.original_pixmap.size()
                
                # 计算缩放比例，留出一些边距
                margin = 20
                width_scale = (viewport_size.width() - margin) / pixmap_size.width()
                height_scale = (viewport_size.height() - margin) / pixmap_size.height()
                
                self.current_scale = min(width_scale, height_scale, 1.0)  # 不超过原始大小
                self.update_image_display()
                
    def original_size(self):
        """原始大小"""
        self.current_scale = 1.0
        self.update_image_display()
        
    def rotate_image(self, angle):
        """旋转图片"""
        self.rotation_angle = (self.rotation_angle + angle) % 360
        self.update_image_display()
        
    def update_image_display(self):
        """更新图片显示"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            try:
                # 应用缩放和旋转
                transform = QTransform()
                transform.scale(self.current_scale, self.current_scale)
                transform.rotate(self.rotation_angle)
                
                # 应用变换
                transformed_pixmap = self.original_pixmap.transformed(
                    transform, Qt.SmoothTransformation
                )
                
                self.image_label.setPixmap(transformed_pixmap)
                
                # 调整label大小以适应图片
                self.image_label.setFixedSize(transformed_pixmap.size())
                
            except Exception as e:
                print(f"更新图片显示时出错: {e}")


class MainWindow(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.ui = None
        self.scanner_thread = None
        self.thumbnail_model = None
        
        # 初始化
        self._init_ui()
        self._init_connections()
        self._init_window()
        self._load_directories()
        self._setup_scanner()
        self._setup_thumbnail_view()
        self._start_background_scan()
        self._load_all_photos()
        
    def _init_ui(self):
        """初始化UI"""
        # 加载UI文件
        ui_file = QFile("main.ui")
        ui_file.open(QIODevice.ReadOnly)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.ui)
        
        # 设置图标
        self.setWindowIcon(qta.icon('fa5s.images', color='#3498db'))
        self._setup_nav_icons()
        self._setup_button_icons()
        self._setup_tree_widget()
        
    def _setup_nav_icons(self):
        """设置导航图标"""
        nav_items = [
            ('fa5s.image', '全部照片'),
            ('fa5s.star', '收藏夹'), 
            ('fa5s.folder', '相册')
        ]
        
        for i, (icon, tooltip) in enumerate(nav_items):
            if i < self.ui.listWidget_main_nav.count():
                item = self.ui.listWidget_main_nav.item(i)
                item.setIcon(qta.icon(icon, color='#ecf0f1'))
                item.setToolTip(tooltip)
    
    def _setup_button_icons(self):
        """设置按钮图标"""
        buttons = {
            'add_dir': ('fa5s.plus-circle', '添加图片目录'),
            'pushButton_refresh': ('fa5s.sync', '刷新数据'),
            'pushButton_settings': ('fa5s.cog', '设置')
        }
        
        for btn_name, (icon, tooltip) in buttons.items():
            btn = getattr(self.ui, btn_name, None)
            if btn:
                btn.setIcon(qta.icon(icon, color='#3498db'))
                btn.setToolTip(tooltip)
    
    def _setup_tree_widget(self):
        """设置TreeWidget"""
        from PySide6.QtGui import QPalette, QColor
        
        tree_widget = self.ui.tree_localdir
        tree_widget.setHeaderLabel("本地目录")
        tree_widget.setRootIsDecorated(True)  # 显示展开/折叠指示器
        tree_widget.setAnimated(True)  # 动画效果
        tree_widget.setSortingEnabled(False)  # 禁用排序，保持自然顺序
        tree_widget.setIndentation(20)  # 缩进宽度
        
        # 设置调色板以确保展开按钮在深色主题下可见
        palette = tree_widget.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#34495e"))  # 背景色
        palette.setColor(QPalette.ColorRole.Text, QColor("#ecf0f1"))  # 文字颜色
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))  # 选中背景
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))  # 选中文本
        palette.setColor(QPalette.ColorRole.Button, QColor("#7f8c8d"))  # 按钮背景
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))  # 按钮文字
        tree_widget.setPalette(palette)
        
        # 简化的样式，避免干扰展开按钮
        tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #34495e;
                border: none;
                outline: none;
                color: #ecf0f1;
                font-size: 13px;
                alternate-background-color: #2c3e50;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #2c3e50;
                min-height: 24px;
            }
            QTreeWidget::item:hover {
                background-color: #3d566e;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:selected:active {
                background-color: #3498db;
            }
            QTreeWidget::item:selected:!active {
                background-color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)

    def _setup_thumbnail_view(self):
        """设置缩略图视图"""
        # 创建模型
        self.thumbnail_model = QStandardItemModel()
        self.ui.thum_body.setModel(self.thumbnail_model)
        
        # 设置视图属性
        self.ui.thum_body.setViewMode(QListView.IconMode)
        self.ui.thum_body.setIconSize(QSize(150, 150))
        self.ui.thum_body.setGridSize(QSize(170, 200))
        self.ui.thum_body.setSpacing(10)
        self.ui.thum_body.setMovement(QListView.Static)
        self.ui.thum_body.setResizeMode(QListView.Adjust)
        self.ui.thum_body.setWrapping(True)
        
        # 设置样式
        self.ui.thum_body.setStyleSheet("""
            QListView {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
            }
            QListView::item {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 5px;
            }
            QListView::item:hover {
                border: 2px solid #3498db;
            }
            QListView::item:selected {
                border: 2px solid #2980b9;
                background-color: #e3f2fd;
            }
        """)
    
    def _init_connections(self):
        """初始化信号连接"""
        self.ui.listWidget_main_nav.currentItemChanged.connect(self._on_nav_changed)
        
        # 连接按钮
        if hasattr(self.ui, 'add_dir'):
            self.ui.add_dir.clicked.connect(self._add_directory)
        if hasattr(self.ui, 'pushButton_refresh'):
            self.ui.pushButton_refresh.clicked.connect(self._refresh_data)
        if hasattr(self.ui, 'pushButton_settings'):
            self.ui.pushButton_settings.clicked.connect(self._open_settings)
            
        # 连接TreeWidget的事件
        if hasattr(self.ui, 'tree_localdir'):
            self.ui.tree_localdir.itemDoubleClicked.connect(self._on_directory_double_clicked)
            self.ui.tree_localdir.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.ui.tree_localdir.customContextMenuRequested.connect(self._show_directory_context_menu)
            self.ui.tree_localdir.itemClicked.connect(self._on_directory_selected)
        
        # 连接缩略图点击事件
        if hasattr(self.ui, 'thum_body'):
            self.ui.thum_body.clicked.connect(self._on_thumbnail_clicked)
            self.ui.thum_body.doubleClicked.connect(self._on_thumbnail_double_clicked)
    
    def _init_window(self):
        """初始化窗口"""
        self.setWindowTitle("图片管理器")
        self.resize(1200, 800)
        self._load_window_state()
        
    def _load_window_state(self):
        """加载窗口状态"""
        try:
            config_file = Path(__file__).parent.parent.parent / "config" / "settings.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f).get('window', {})
                    self.resize(config.get('width', 1200), config.get('height', 800))
                    self.move(config.get('x', 100), config.get('y', 100))
        except Exception:
            pass
    
    def _save_window_state(self):
        """保存窗口状态"""
        try:
            config_file = Path(__file__).parent.parent.parent / "config" / "settings.json"
            config = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['window'] = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _on_nav_changed(self, current, previous):
        """导航切换"""
        if not current:
            return
        
        nav_text = current.text()
        nav_map = {
            "全部照片": self._load_all_photos,
            "收藏夹": self._load_favorites,
            "相册": self._load_albums
        }
        
        action = nav_map.get(nav_text)
        if action:
            action()
            
        # 更新标签显示
        self.ui.label_gridstate.setText(nav_text)
        self._update_photo_count(nav_text)
    
    def _add_directory(self):
        """添加目录到数据库并自动扫描"""
        if not DatabaseInitializer.check_database_health()['healthy']:
            QMessageBox.warning(self, "警告", "数据库未初始化")
            return
        
        directory = QFileDialog.getExistingDirectory(self, "选择图片目录")
        if directory:
            try:
                # 规范化路径，确保格式一致
                import os
                normalized_path = os.path.normpath(directory)
                
                # 检查目录是否已存在
                with next(get_db()) as db:
                    existing = db.query(Directory).filter(Directory.path == normalized_path).first()
                    if existing:
                        QMessageBox.warning(self, "警告", "该目录已存在！")
                        return
                    
                    # 添加到数据库
                    dir_name = os.path.basename(normalized_path)
                    new_dir = Directory(path=normalized_path, name=dir_name)
                    db.add(new_dir)
                    db.commit()
                    
                    # 刷新TreeWidget显示
                    self._refresh_directories()
                    
                    # 自动启动扫描新添加的目录
                    self._scan_single_directory(normalized_path, dir_name)
                    
                    QMessageBox.information(self, "成功", f"已添加目录: {dir_name}，正在扫描图片...")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加目录失败: {str(e)}")
                
    def _scan_single_directory(self, directory_path, dir_name):
        """扫描单个目录"""
        if not os.path.exists(directory_path):
            return
            
        self.status_label.setText(f"正在扫描目录: {dir_name}...")
        self.progress_bar.setVisible(True)
        
        # 创建并启动扫描线程
        self.scanner_thread = ImageScannerThread([directory_path])
        self.scanner_thread.progress_updated.connect(self._on_scan_progress)
        self.scanner_thread.scan_completed.connect(
            lambda count: self._on_single_scan_completed(count, dir_name)
        )
        self.scanner_thread.scan_error.connect(self._on_scan_error)
        self.scanner_thread.start()
        
    def _on_single_scan_completed(self, count, dir_name):
        """单个目录扫描完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"扫描完成：{dir_name} ({count} 张图片)")
        QMessageBox.information(self, "扫描完成", f"目录 {dir_name} 扫描完成，共发现 {count} 张图片")
    
    def _load_directories(self):
        """从数据库加载目录到TreeWidget，包含子目录"""
        try:
            with next(get_db()) as db:
                directories = db.query(Directory).filter(Directory.is_active == True).all()
                
                tree_widget = self.ui.tree_localdir
                tree_widget.clear()
                
                for directory in directories:
                    if os.path.exists(directory.path):
                        # 创建根目录项
                        root_item = QTreeWidgetItem()
                        root_item.setText(0, directory.name)
                        root_item.setData(0, Qt.ItemDataRole.UserRole, directory.path)  # 使用UserRole存储路径
                        root_item.setToolTip(0, directory.path)
                        root_item.setIcon(0, qta.icon('fa5s.folder', color='#3498db'))
                        
                        # 递归加载子目录
                        self._load_subdirectories(root_item, directory.path)
                        
                        tree_widget.addTopLevelItem(root_item)
                        # 默认不展开根目录
                        root_item.setExpanded(False)
                    else:
                        # 目录不存在，显示警告图标
                        root_item = QTreeWidgetItem()
                        root_item.setText(0, f"{directory.name} (路径不存在)")
                        root_item.setData(0, Qt.ItemDataRole.UserRole, directory.path)  # 使用UserRole存储路径
                        root_item.setIcon(0, qta.icon('fa5s.exclamation-triangle', color='#e74c3c'))
                        tree_widget.addTopLevelItem(root_item)
                        
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载目录失败: {str(e)}")
    
    def _load_subdirectories(self, parent_item, parent_path):
        """递归加载子目录"""
        try:
            # 获取子目录列表，忽略隐藏文件夹（以.开头）
            subdirs = [d for d in os.listdir(parent_path) 
                      if os.path.isdir(os.path.join(parent_path, d)) and 
                      not d.startswith('.')]
            
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(parent_path, subdir)
                
                # 创建子目录项
                child_item = QTreeWidgetItem()
                child_item.setText(0, subdir)
                child_item.setData(0, Qt.ItemDataRole.UserRole, subdir_path)
                child_item.setToolTip(0, subdir_path)
                child_item.setIcon(0, qta.icon('fa5s.folder', color='#95a5a6'))
                
                parent_item.addChild(child_item)
                
                # 继续递归加载更深层的子目录
                # 限制递归深度，避免性能问题
                if subdir_path.count(os.sep) - parent_path.count(os.sep) < 3:
                    self._load_subdirectories(child_item, subdir_path)
                    
        except (PermissionError, OSError):
            # 忽略权限错误或其他文件系统错误
            pass
    
    def _refresh_directories(self):
        """刷新目录显示"""
        self._load_directories()
    
    def _refresh_data(self):
        """刷新数据 - 重新生成缩略图"""
        reply = QMessageBox.question(
            self, "确认刷新", 
            "确定要重新生成所有缩略图吗？\n\n"
            "这将删除现有缩略图并重新生成，\n"
            "可以修复图片方向显示问题。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除现有缩略图文件和记录
                import shutil
                thumbnails_dir = Path("thumbnails")
                if thumbnails_dir.exists():
                    shutil.rmtree(thumbnails_dir)
                
                # 删除数据库中的缩略图记录
                with next(get_db()) as db:
                    db.query(Thumbnail).delete()
                    db.commit()
                
                # 重新扫描图片
                self._start_background_scan()
                QMessageBox.information(self, "提示", "正在重新生成缩略图，请稍候...")
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"刷新失败: {str(e)}")
    
    def _load_all_photos(self):
        """加载所有照片"""
        self._update_status("显示所有照片")
        self._update_photo_count_for_all()
        self._load_thumbnails_for_all()

    def _load_favorites(self):
        """加载收藏照片"""
        self._update_status("显示收藏照片")
        self._update_photo_count_for_favorites()
        self._load_thumbnails_for_favorites()

    def _load_albums(self):
        """加载相册"""
        self._update_status("显示相册")
        self._update_photo_count_for_albums()
        self._load_thumbnails_for_albums()

    def _update_photo_count(self, nav_text):
        """根据导航类型更新图片数量"""
        try:
            with next(get_db()) as db:
                if nav_text == "全部照片":
                    count = db.query(Image).count()
                elif nav_text == "收藏夹":
                    count = db.query(Image).filter(Image.is_favorite == True).count()
                elif nav_text == "相册":
                    # 这里可能需要根据相册逻辑调整
                    count = 0  # 暂时返回0，后续实现相册功能
                else:
                    count = 0
                
                self.ui.label_photo_count.setText(f"{count} 张照片")
        except Exception as e:
            print(f"更新图片数量失败: {e}")
            self.ui.label_photo_count.setText("0 张照片")

    def _update_photo_count_for_directory(self, directory_path):
        """更新指定目录及其子目录的图片数量"""
        try:
            import os
            normalized_path = os.path.normpath(str(directory_path))
            
            with next(get_db()) as db:
                # 使用路径前缀匹配来获取目录及其子目录的所有图片
                search_pattern = f"{normalized_path}%"
                images = db.query(Image).filter(
                    Image.file_path.like(search_pattern)
                ).all()
                
                count = len(images) if images else 0
                self.ui.label_photo_count.setText(f"{count} 张照片")
        except Exception as e:
            print(f"更新目录图片数量失败: {e}")
            self.ui.label_photo_count.setText("0 张照片")

    def _update_photo_count_for_all(self):
        """更新所有照片的数量"""
        self._update_photo_count("全部照片")

    def _update_photo_count_for_favorites(self):
        """更新收藏照片的数量"""
        self._update_photo_count("收藏夹")

    def _update_photo_count_for_albums(self):
        """更新相册的数量"""
        self._update_photo_count("相册")

    def _load_thumbnails_for_all(self):
        """加载所有照片的缩略图"""
        self._load_thumbnails_from_query(lambda db: db.query(Image).all())

    def _load_thumbnails_for_favorites(self):
        """加载收藏照片的缩略图"""
        self._load_thumbnails_from_query(lambda db: db.query(Image).filter(Image.is_favorite == True).all())

    def _load_thumbnails_for_albums(self):
        """加载相册的缩略图"""
        # 相册功能暂未实现，显示空
        self.thumbnail_model.clear()

    def _load_thumbnails_for_directory(self, directory_path):
        """加载指定目录及其子目录的缩略图"""
        try:
            import os
            normalized_path = os.path.normpath(str(directory_path))
            
            with next(get_db()) as db:
                # 使用路径前缀匹配来获取目录及其子目录的所有图片
                search_pattern = f"{normalized_path}%"
                images = db.query(Image).filter(
                    Image.file_path.like(search_pattern)
                ).all()
                
                if images:
                    self._display_thumbnails(images)
                else:
                    # 如果没有找到图片，检查是否是已注册的目录
                    directory = db.query(Directory).filter(Directory.path == normalized_path).first()
                    if directory:
                        # 获取该目录的图片
                        images = db.query(Image).filter(Image.directory_id == directory.id).all()
                        self._display_thumbnails(images)
                    else:
                        self.thumbnail_model.clear()
        except Exception as e:
            print(f"加载目录缩略图失败: {e}")
            self.thumbnail_model.clear()

    def _load_thumbnails_from_query(self, query_func):
        """从查询函数加载缩略图"""
        try:
            with next(get_db()) as db:
                images = query_func(db)
                self._display_thumbnails(images)
        except Exception as e:
            print(f"加载缩略图失败: {e}")
            self.thumbnail_model.clear()

    def _get_rotation_angle(self, orientation_str):
        """根据EXIF方向信息获取旋转角度"""
        if not orientation_str:
            return 0
            
        orientation_map = {
            'Horizontal (normal)': 0,
            'Rotate 90 CW': 90,
            'Rotate 180': 180,
            'Rotate 270 CW': 270,
            'Mirror horizontal': 0,  # 不处理镜像
            'Mirror vertical': 0,      # 不处理镜像
            'Mirror horizontal and rotate 270 CW': 0,  # 不处理镜像
            'Mirror horizontal and rotate 90 CW': 0    # 不处理镜像
        }
        
        return orientation_map.get(orientation_str, 0)
    
    def _rotate_pixmap(self, pixmap, angle):
        """旋转QPixmap"""
        if angle == 0:
            return pixmap
            
        transform = QtGui.QTransform()
        transform.rotate(angle)
        return pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
    
    def _display_thumbnails(self, images):
        """显示缩略图（带方向修正）"""
        self.thumbnail_model.clear()
        
        for image in images:
            try:
                # 获取缩略图路径
                with next(get_db()) as db:
                    thumbnail = db.query(Thumbnail).filter(Thumbnail.image_id == image.id).first()
                    thumbnail_path = thumbnail.thumbnail_path if thumbnail else None
                
                if thumbnail_path and os.path.exists(thumbnail_path):
                    # 创建缩略图项
                    item = QStandardItem()
                    
                    # 加载缩略图
                    pixmap = QPixmap(thumbnail_path)
                    if not pixmap.isNull():
                        # 根据EXIF方向信息旋转缩略图
                        rotation_angle = self._get_rotation_angle(image.orientation)
                        if rotation_angle != 0:
                            pixmap = self._rotate_pixmap(pixmap, rotation_angle)
                        item.setIcon(pixmap)
                    else:
                        # 如果缩略图加载失败，使用占位符
                        item.setIcon(qta.icon('fa5s.image', color='#95a5a6', scale_factor=1.5))
                else:
                    # 没有缩略图，使用占位符
                    item.setIcon(qta.icon('fa5s.image', color='#95a5a6', scale_factor=1.5))
                
                # 设置文件名作为文本
                item.setText(image.file_name)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setData(image.file_path, Qt.ItemDataRole.UserRole)  # 存储完整路径
                item.setData(image.id, Qt.ItemDataRole.UserRole + 1)  # 存储图片ID
                
                self.thumbnail_model.appendRow(item)
                
            except Exception as e:
                print(f"加载缩略图项失败: {e}")
    
    def _open_settings(self):
        """打开设置"""
        QMessageBox.information(self, "设置", "设置功能开发中...")
    
    def _on_directory_double_clicked(self, item):
        """双击目录项"""
        directory_path = item.data(0, Qt.ItemDataRole.UserRole)
        if directory_path and os.path.exists(str(directory_path)):
            # 展开或折叠目录
            item.setExpanded(not item.isExpanded())
            
            # 如果是根目录项，刷新子目录
            if item.parent() is None:  # 顶层目录
                self._refresh_directory_item(item, str(directory_path))
        else:
            QMessageBox.warning(self, "警告", f"目录不存在: {directory_path}")
    
    def _on_directory_selected(self, item):
        """目录被选中"""
        directory_path = item.data(0, Qt.ItemDataRole.UserRole)
        if directory_path and os.path.exists(str(directory_path)):
            # 获取目录名称
            directory_name = os.path.basename(str(directory_path))
            if not directory_name:  # 根目录的情况
                directory_name = str(directory_path)
            
            # 更新标签显示
            self.ui.label_gridstate.setText(directory_name)
            self._update_photo_count_for_directory(str(directory_path))
            self._load_thumbnails_for_directory(str(directory_path))
    
    def _show_directory_context_menu(self, position):
        """显示目录右键菜单"""
        tree_widget = self.ui.tree_localdir
        item = tree_widget.itemAt(position)
        
        if item is None:
            return
            
        # 判断是否是根目录
        is_root = item.parent() is None
        
        menu = QMenu(self)
        
        # 添加菜单项
        open_action = menu.addAction(qta.icon('fa5s.folder-open', color='#3498db'), "打开目录")
        refresh_action = menu.addAction(qta.icon('fa5s.sync', color='#3498db'), "刷新")
        
        # 只为根目录显示移除选项
        if is_root:
            remove_action = menu.addAction(qta.icon('fa5s.trash', color='#e74c3c'), "从列表移除")
        
        # 显示菜单
        action = menu.exec(tree_widget.mapToGlobal(position))
        
        directory_path = str(item.data(0, Qt.ItemDataRole.UserRole))
        if action == open_action:
            self._open_directory(item)
        elif action == refresh_action:
            self._refresh_directory_item(item, directory_path)
        elif is_root and action == menu.actions()[-1]:  # 最后一个动作是移除
            self._remove_directory(item)
    
    def _open_directory(self, item):
        """打开目录"""
        directory_path = item.data(0, 1)
        if os.path.exists(directory_path):
            import subprocess
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', directory_path])
                else:  # macOS/Linux
                    subprocess.run(['open', directory_path])
            except Exception as e:
                QMessageBox.warning(self, "警告", f"无法打开目录: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "目录不存在")
    
    def _refresh_directory_item(self, item, directory_path):
        """刷新指定目录的子目录"""
        if not os.path.exists(directory_path):
            return
            
        # 清除现有子项
        item.takeChildren()
        
        # 重新加载子目录
        try:
            subdirs = [d for d in os.listdir(directory_path) 
                      if os.path.isdir(os.path.join(directory_path, d))]
            
            for subdir in sorted(subdirs):
                subdir_path = os.path.join(directory_path, subdir)
                child_item = QTreeWidgetItem()
                child_item.setText(0, subdir)
                child_item.setData(0, 1, subdir_path)
                child_item.setToolTip(0, subdir_path)
                child_item.setIcon(0, qta.icon('fa5s.folder', color='#95a5a6'))
                item.addChild(child_item)
                
                # 如果子目录也有子目录，添加一个占位符
                if any(os.path.isdir(os.path.join(subdir_path, d)) 
                       for d in os.listdir(subdir_path)):
                    placeholder = QTreeWidgetItem()
                    placeholder.setText(0, "...")
                    child_item.addChild(placeholder)
                    
        except (PermissionError, OSError):
            pass
    
    def _remove_directory(self, item):
        """从数据库移除根目录"""
        directory_path = str(item.data(0, Qt.ItemDataRole.UserRole))  # 确保获取字符串路径
        
        try:
            with next(get_db()) as db:
                # 使用规范化路径进行匹配，确保路径格式一致
                import os
                normalized_path = os.path.normpath(directory_path)
                
                directory = db.query(Directory).filter(
                    Directory.path == normalized_path,
                    Directory.is_active == True
                ).first()
                
                if directory:
                    # 确认删除
                    reply = QMessageBox.question(
                        self, "确认删除", 
                        f"确定要从数据库中完全删除目录 '{directory.name}' 吗？\n\n"
                        f"路径: {directory.path}\n\n"
                        f"注意：此操作将同时删除该目录下的所有图片记录！",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        # 获取该目录下的所有图片信息
                        images = db.query(Image).filter(Image.directory_id == directory.id).all()
                        image_ids = [img.id for img in images]
                        
                        # 收集需要删除的缩略图文件路径
                        thumbnail_paths = []
                        if image_ids:
                            thumbnails = db.query(Thumbnail).filter(Thumbnail.image_id.in_(image_ids)).all()
                            thumbnail_paths = [thumb.thumbnail_path for thumb in thumbnails if thumb.thumbnail_path and os.path.exists(thumb.thumbnail_path)]
                        
                        # 删除生成的缩略图文件
                        import os
                        for thumb_path in thumbnail_paths:
                            try:
                                os.remove(thumb_path)
                            except (OSError, IOError) as e:
                                # 如果删除失败，记录错误但不中断流程
                                print(f"删除缩略图文件失败: {thumb_path} - {e}")
                        
                        # 删除相关的缩略图数据库记录
                        if image_ids:
                            db.query(Thumbnail).filter(Thumbnail.image_id.in_(image_ids)).delete(synchronize_session=False)
                        
                        # 删除该目录下的所有图片数据库记录
                        db.query(Image).filter(Image.directory_id == directory.id).delete(synchronize_session=False)
                        
                        # 删除目录数据库记录
                        db.delete(directory)
                        db.commit()
                        
                        # 刷新显示
                        self._refresh_directories()
                        QMessageBox.information(self, "成功", "目录及相关记录已删除，本地图片文件保留")
                else:
                    # 获取所有活跃目录供用户参考
                    active_dirs = db.query(Directory).filter(Directory.is_active == True).all()
                    paths = [d.path for d in active_dirs]
                    QMessageBox.warning(
                        self, "警告", 
                        f"未找到对应的目录记录: {directory_path}\n\n"
                        f"数据库中的活跃路径:\n" + "\n".join(paths)
                    )
                    
        except Exception as e:
            QMessageBox.warning(self, "警告", f"移除目录失败: {str(e)}")

    def _setup_scanner(self):
        """设置后台扫描器"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        self.status_label = QLabel("准备就绪")
        self.statusBar().addWidget(self.status_label)

    def _start_background_scan(self):
        """启动后台扫描"""
        try:
            with next(get_db()) as db:
                # 获取所有活跃目录
                directories = db.query(Directory).filter(Directory.is_active == True).all()
                directory_paths = [d.path for d in directories if os.path.exists(d.path)]
                
                if directory_paths:
                    self.status_label.setText("正在扫描图片...")
                    self.progress_bar.setVisible(True)
                    
                    # 创建并启动扫描线程
                    self.scanner_thread = ImageScannerThread(directory_paths)
                    self.scanner_thread.progress_updated.connect(self._on_scan_progress)
                    self.scanner_thread.scan_completed.connect(self._on_scan_completed)
                    self.scanner_thread.scan_error.connect(self._on_scan_error)
                    self.scanner_thread.start()
                else:
                    self.status_label.setText("没有找到可扫描的目录")
                    
        except Exception as e:
            self.status_label.setText(f"扫描初始化失败: {str(e)}")

    def _on_scan_progress(self, current, total):
        """扫描进度更新"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"扫描图片... {current}/{total}")

    def _on_scan_completed(self, count):
        """扫描完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"扫描完成，共处理 {count} 张图片")

    def _on_scan_error(self, error_msg):
        """扫描错误"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("扫描错误")
        QMessageBox.warning(self, "扫描错误", error_msg)

    def _on_thumbnail_clicked(self, index):
        """处理缩略图点击事件，显示图片详情"""
        if not index.isValid():
            return
            
        # 获取图片ID和文件路径
        image_id = index.data(Qt.ItemDataRole.UserRole + 1)
        file_path = index.data(Qt.ItemDataRole.UserRole)
        
        if not image_id or not file_path:
            return
            
        try:
            # 从数据库获取图片详细信息
            with next(get_db()) as db:
                image = db.query(Image).filter(Image.id == image_id).first()
                if not image:
                    return
                
                # 显示图片预览
                self._display_image_preview(file_path, image.orientation)
                
                # 显示EXIF信息
                self._display_exif_info(image)
                
        except Exception as e:
            print(f"显示图片详情失败: {e}")

    def _on_thumbnail_double_clicked(self, index):
        """处理缩略图双击事件，打开完整图片预览窗口"""
        try:
            if not index.isValid():
                return
                
            # 获取图片文件路径
            item = self.thumbnail_model.itemFromIndex(index)
            if not item:
                return
                
            image_path = item.data(Qt.UserRole)
            if not image_path or not os.path.exists(image_path):
                QMessageBox.warning(self, "警告", "图片文件不存在")
                return
                
            # 创建并显示图片预览窗口
            preview_window = ImagePreviewWindow(image_path, self)
            preview_window.exec_()  # 模态显示
            
        except Exception as e:
            print(f"打开图片预览失败: {e}")
            QMessageBox.warning(self, "错误", f"无法打开图片预览: {str(e)}")

    def _display_image_preview(self, file_path, orientation):
        """显示图片预览"""
        try:
            if hasattr(self.ui, 'image_preview'):
                # 加载图片
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 根据EXIF方向信息旋转图片
                    rotation_angle = self._get_rotation_angle(orientation)
                    if rotation_angle != 0:
                        pixmap = self._rotate_pixmap(pixmap, rotation_angle)
                    
                    # 缩放图片以适应预览区域
                    if hasattr(self.ui, 'preview_container'):
                        preview_size = self.ui.preview_container.size()
                        scaled_pixmap = pixmap.scaled(
                            preview_size, 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.ui.image_preview.setPixmap(scaled_pixmap)
                        self.ui.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            print(f"显示图片预览失败: {e}")

    def _display_exif_info(self, image):
        """显示EXIF信息，处理所有可能的缺失值和字符编码问题"""
        try:
            def clean_text(text, default="未知"):
                """彻底清理文本，确保只包含可显示的字符"""
                if text is None:
                    return default
                try:
                    # 转换为字符串并去除空白
                    str_text = str(text).strip()
                    
                    # 检查是否为无效值
                    if not str_text or str_text.lower() in ['none', 'null', 'undefined', '']:
                        return default
                    
                    # 检查是否包含非打印字符
                    import re
                    # 移除非打印字符和控制字符，但保留常见标点符号
                    clean_str = re.sub(r'[^\x20-\x7E\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', '', str_text)
                    
                    # 如果清理后为空，返回默认值
                    if not clean_str.strip():
                        return default
                    
                    return clean_str.strip()
                except Exception:
                    return default
            
            def safe_display(value, prefix="", suffix="", default="未知"):
                """安全显示带前缀后缀的值"""
                clean_value = clean_text(value, default)
                if clean_value == default:
                    return default
                return f"{prefix}{clean_value}{suffix}"
            
            # 基本信息显示
            if hasattr(self.ui, 'value_filename'):
                filename = clean_text(image.file_name)
                self.ui.value_filename.setText(f"文件名: {filename}")
            
            if hasattr(self.ui, 'value_dimensions'):
                try:
                    width = int(image.width) if image.width and str(image.width).strip().isdigit() else None
                    height = int(image.height) if image.height and str(image.height).strip().isdigit() else None
                    if width and height:
                        dimensions = f"尺寸: {width} × {height}"
                    else:
                        dimensions = "尺寸: 未知"
                except:
                    dimensions = "尺寸: 未知"
                self.ui.value_dimensions.setText(dimensions)
            
            # 相机信息显示
            if hasattr(self.ui, 'value_camera_model'):
                make = clean_text(image.camera_make)
                model = clean_text(image.camera_model)
                if make != "未知" and model != "未知":
                    camera_info = f"{make} {model}"
                elif make != "未知":
                    camera_info = make
                elif model != "未知":
                    camera_info = model
                else:
                    camera_info = "未知"
                self.ui.value_camera_model.setText(camera_info)
            
            if hasattr(self.ui, 'value_lens'):
                lens = clean_text(image.lens_model)
                self.ui.value_lens.setText(lens)
            
            if hasattr(self.ui, 'value_date'):
                date_str = "未知"
                if image.date_taken:
                    try:
                        from datetime import datetime
                        if isinstance(image.date_taken, str):
                            # 如果是字符串，尝试解析
                            date_str = image.date_taken.strip()
                            if len(date_str) < 3:  # 太短，可能是无效值
                                date_str = "未知"
                        else:
                            # 如果是datetime对象
                            date_str = image.date_taken.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        date_str = "未知"
                elif image.created_at:
                    try:
                        date_str = image.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        date_str = "未知"
                else:
                    date_str = "未知"
                self.ui.value_date.setText(date_str)
            
            # 曝光参数显示
            if hasattr(self.ui, 'value_aperture'):
                try:
                    aperture = float(str(image.aperture).strip())
                    if aperture > 0:
                        aperture_str = f"f/{aperture:.1f}"
                    else:
                        aperture_str = "未知"
                except:
                    aperture_str = "未知"
                self.ui.value_aperture.setText(aperture_str)
            
            if hasattr(self.ui, 'value_shutter'):
                shutter = clean_text(image.shutter_speed)
                self.ui.value_shutter.setText(shutter)
            
            if hasattr(self.ui, 'value_iso'):
                try:
                    iso = int(str(image.iso).strip())
                    if iso > 0:
                        iso_str = f"ISO {iso}"
                    else:
                        iso_str = "未知"
                except:
                    iso_str = "未知"
                self.ui.value_iso.setText(iso_str)
            
            if hasattr(self.ui, 'value_focal'):
                try:
                    focal = float(str(image.focal_length).strip())
                    focal_35 = float(str(image.focal_length_35mm).strip()) if image.focal_length_35mm else None
                    if focal > 0:
                        if focal_35 and focal_35 > 0:
                            focal_str = f"{int(focal)}mm (35mm等效: {int(focal_35)}mm)"
                        else:
                            focal_str = f"{int(focal)}mm"
                    else:
                        focal_str = "未知"
                except:
                    focal_str = "未知"
                self.ui.value_focal.setText(focal_str)
            
            # GPS信息显示
            if hasattr(self.ui, 'value_gps'):
                try:
                    lat = float(str(image.gps_latitude).strip()) if image.gps_latitude else None
                    lon = float(str(image.gps_longitude).strip()) if image.gps_longitude else None
                    alt = float(str(image.gps_altitude).strip()) if image.gps_altitude else None
                    
                    if lat is not None and lon is not None:
                        gps_text = f"{lat:.6f}, {lon:.6f}"
                        if alt is not None and abs(alt) > 0.1:
                            gps_text += f" (海拔: {int(alt)}m)"
                    else:
                        gps_text = "未知"
                except:
                    gps_text = "未知"
                self.ui.value_gps.setText(gps_text)
                
        except Exception as e:
            print(f"显示EXIF信息失败: {e}")

    def _update_status(self, message):
        """更新状态"""
        if hasattr(self.ui, 'statusbar'):
            self.ui.statusbar.showMessage(message, 3000)

    def closeEvent(self, event):
        """关闭事件"""
        self._save_window_state()
        event.accept()


class AppManager:
    """应用管理器"""
    
    def __init__(self):
        self.app = None
        self.window = None
    
    def run(self):
        """运行应用"""
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        # 初始化数据库
        if not DatabaseInitializer.initialize_database():
            QMessageBox.critical(None, "错误", "数据库初始化失败")
            return False
        
        # 检查数据库健康状态
        health = DatabaseInitializer.check_database_health()
        if not health['healthy']:
            QMessageBox.warning(None, "警告", "数据库异常")
        
        # 创建主窗口
        self.window = MainWindow()
        self.window.show()
        
        return self.app.exec()
    
    def get_app(self):
        return self.app
    
    def get_window(self):
        return self.window


if __name__ == "__main__":
    manager = AppManager()
    sys.exit(manager.run())