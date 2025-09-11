"""
主窗口类
负责应用的主界面和交互逻辑
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, 
                             QPushButton, QToolButton, QMessageBox, QFileDialog)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer
import qtawesome as qta

from src.core.initializer import get_initializer
from src.core.db_operations import DirectoryOperations, ImageOperations


class MainWindow(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化UI
        self._setup_ui()
        self._setup_icons()
        self._setup_connections()
        self._setup_styles()
        
        # 数据相关
        self.current_directory = None
        self.image_operations = None
        self.directory_operations = None
        
        # 初始化数据操作
        self._init_data_operations()
        
        # 设置窗口属性
        self._setup_window_properties()
        
        # 加载初始数据
        self._load_initial_data()
    
    def _setup_ui(self):
        """设置UI界面"""
        ui_file = QFile("main.ui")
        ui_file.open(QIODevice.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        self.setCentralWidget(self.ui)
    
    def _setup_icons(self):
        """设置界面图标"""
        # 应用图标
        self.setWindowIcon(qta.icon('fa5s.images', color='#3498db'))
        
        # 导航图标
        nav_icons = [
            ('fa5s.image', '全部照片'),
            ('fa5s.star', '收藏夹'),
            ('fa5s.folder', '相册')
        ]
        
        for i, (icon_name, tooltip) in enumerate(nav_icons):
            if i < self.ui.listWidget_main_nav.count():
                self.ui.listWidget_main_nav.item(i).setIcon(
                    qta.icon(icon_name, color='#ecf0f1')
                )
                self.ui.listWidget_main_nav.item(i).setToolTip(tooltip)
        
        # 按钮图标
        if hasattr(self.ui, 'add_dir'):
            self.ui.add_dir.setIcon(qta.icon('fa5s.plus-circle', color='#3498db'))
            self.ui.add_dir.setToolTip("添加图片目录")
        
        if hasattr(self.ui, 'pushButton_refresh'):
            self.ui.pushButton_refresh.setIcon(qta.icon('fa5s.sync', color='#7f8c8d'))
            self.ui.pushButton_refresh.setToolTip("刷新数据")
        
        if hasattr(self.ui, 'pushButton_settings'):
            self.ui.pushButton_settings.setIcon(qta.icon('fa5s.cog', color='#ecf0f1'))
            self.ui.pushButton_settings.setToolTip("设置")
    
    def _setup_connections(self):
        """连接信号和槽"""
        # 导航切换
        self.ui.listWidget_main_nav.currentItemChanged.connect(self._on_nav_changed)
        
        # 按钮连接
        if hasattr(self.ui, 'add_dir'):
            self.ui.add_dir.clicked.connect(self._add_directory)
        
        if hasattr(self.ui, 'pushButton_refresh'):
            self.ui.pushButton_refresh.clicked.connect(self._refresh_data)
        
        if hasattr(self.ui, 'pushButton_settings'):
            self.ui.pushButton_settings.clicked.connect(self._open_settings)
    
    def _setup_styles(self):
        """设置样式"""
        # 设置按钮样式
        settings_style = """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        """
        
        if hasattr(self.ui, 'pushButton_settings'):
            self.ui.pushButton_settings.setStyleSheet(settings_style)
    
    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("图片管理器")
        self.resize(1200, 800)
        
        # 从配置文件加载窗口状态
        self._load_window_state()
    
    def _init_data_operations(self):
        """初始化数据操作"""
        # DirectoryOperations 和 ImageOperations 都是静态方法类，不需要实例化
        # 直接通过类名调用即可
    
    def _load_initial_data(self):
        """加载初始数据"""
        if self.directory_operations:
            stats = get_initializer().get_database_stats()
            print(f"📊 应用数据: {stats}")
            self._update_status_bar(f"就绪 - 共 {stats['images']} 张图片")
    
    def _load_window_state(self):
        """从配置文件加载窗口状态"""
        try:
            import json
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                if 'window' in config:
                    window_config = config['window']
                    self.resize(
                        window_config.get('width', 1200),
                        window_config.get('height', 800)
                    )
                    self.move(
                        window_config.get('x', 100),
                        window_config.get('y', 100)
                    )
        except Exception as e:
            print(f"加载窗口状态失败: {e}")
    
    def _save_window_state(self):
        """保存窗口状态到配置文件"""
        try:
            import json
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.json"
            
            # 读取现有配置
            config = {}
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 更新窗口配置
            config['window'] = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存窗口状态失败: {e}")
    
    def _on_nav_changed(self, current, previous):
        """导航切换处理"""
        if not current:
            return
            
        nav_text = current.text()
        print(f"切换到: {nav_text}")
        
        # 根据导航类型加载对应数据
        if "全部照片" in nav_text:
            self._load_all_photos()
        elif "收藏夹" in nav_text:
            self._load_favorites()
        elif "相册" in nav_text:
            self._load_albums()
    
    def _add_directory(self):
        """添加目录"""
        if not get_initializer().get_db_manager():
            QMessageBox.warning(self, "警告", "数据库未连接")
            return
        
        directory = QFileDialog.getExistingDirectory(
            self, "选择图片目录", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            try:
                # 添加目录到数据库
                dir_data = DirectoryOperations.add_directory(directory, "用户添加")
                if dir_data:
                    QMessageBox.information(
                        self, "成功", 
                        f"已添加目录: {directory}\n目录ID: {dir_data['id']}"
                    )
                    self._refresh_data()
                else:
                    QMessageBox.warning(self, "警告", "目录已存在或添加失败")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加目录失败: {e}")
    
    def _refresh_data(self):
        """刷新数据"""
        self._load_initial_data()
        self._update_status_bar("数据已刷新")
    
    def _open_settings(self):
        """打开设置"""
        QMessageBox.information(self, "设置", "设置功能开发中...")
    
    def _load_all_photos(self):
        """加载所有照片"""
        if not self.image_operations:
            return
        
        try:
            # TODO: 实现图片加载逻辑
            print("加载所有照片...")
            self._update_status_bar("显示所有照片")
        except Exception as e:
            print(f"加载照片失败: {e}")
    
    def _load_favorites(self):
        """加载收藏照片"""
        # TODO: 实现收藏夹逻辑
        print("加载收藏照片...")
        self._update_status_bar("显示收藏照片")
    
    def _load_albums(self):
        """加载相册"""
        # TODO: 实现相册逻辑
        print("加载相册...")
        self._update_status_bar("显示相册")
    
    def _update_status_bar(self, message):
        """更新状态栏"""
        if hasattr(self.ui, 'statusbar'):
            self.ui.statusbar.showMessage(message, 3000)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self._save_window_state()
        event.accept()


class AppManager:
    """应用管理器"""
    
    def __init__(self):
        self.app = None
        self.window = None
    
    def run(self):
        """运行应用"""
        # 创建应用
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        # 初始化应用
        initializer = get_initializer()
        if not initializer.initialize_all():
            print("❌ 应用初始化失败，无法启动")
            return False
        
        # 创建主窗口
        self.window = MainWindow()
        self.window.show()
        
        # 运行事件循环
        return self.app.exec()
    
    def get_app(self):
        """获取QApplication实例"""
        return self.app
    
    def get_window(self):
        """获取主窗口实例"""
        return self.window