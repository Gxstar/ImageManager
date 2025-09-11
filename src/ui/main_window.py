"""
主窗口类 - 简洁版本
负责应用的主界面和交互逻辑
"""

import sys
from pathlib import Path
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, 
                             QMessageBox, QFileDialog)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
import qtawesome as qta

from src.core.initializer import DatabaseInitializer


class MainWindow(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.ui = None
        
        # 初始化
        self._init_ui()
        self._init_connections()
        self._init_window()
        
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
        
        nav_map = {
            "全部照片": self._load_all_photos,
            "收藏夹": self._load_favorites,
            "相册": self._load_albums
        }
        
        action = nav_map.get(current.text())
        if action:
            action()
    
    def _add_directory(self):
        """添加目录"""
        if not DatabaseInitializer.check_database_health()['healthy']:
            QMessageBox.warning(self, "警告", "数据库未初始化")
            return
        
        directory = QFileDialog.getExistingDirectory(self, "选择图片目录")
        if directory:
            QMessageBox.information(self, "提示", f"已选择: {directory}")
            self._refresh_data()
    
    def _refresh_data(self):
        """刷新数据"""
        health = DatabaseInitializer.check_database_health()
        message = f"数据库健康: {health['tables_count']} 个表"
        self._update_status(message)
    
    def _load_all_photos(self):
        """加载所有照片"""
        self._update_status("显示所有照片")
    
    def _load_favorites(self):
        """加载收藏照片"""
        self._update_status("显示收藏照片")
    
    def _load_albums(self):
        """加载相册"""
        self._update_status("显示相册")
    
    def _open_settings(self):
        """打开设置"""
        QMessageBox.information(self, "设置", "设置功能开发中...")
    
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