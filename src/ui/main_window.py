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
                             QMessageBox, QTreeWidgetItem, QMenu, QProgressBar, QLabel)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QFontDatabase
import PySide6.QtGui as QtGui
from src.core.scanner_thread import ImageScannerThread
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
import qtawesome as qta

from src.core.initializer import DatabaseInitializer
from src.core.database import get_db
from src.models.directory import Directory


class MainWindow(QMainWindow):
    """主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.ui = None
        self.scanner_thread = None
        
        # 初始化
        self._init_ui()
        self._init_connections()
        self._init_window()
        self._load_directories()
        self._setup_scanner()
        self._start_background_scan()
        
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
        """添加目录到数据库"""
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
                    
                    QMessageBox.information(self, "成功", f"已添加目录: {dir_name}")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加目录失败: {str(e)}")
    
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
        """刷新数据"""
        health = DatabaseInitializer.check_database_health()
        message = f"数据库健康: {health['tables_count']} 个表"
        self._update_status(message)
        self._refresh_directories()
    
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
                        f"确定要从列表中移除目录 '{directory.name}' 吗？\n\n路径: {directory.path}",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        directory.is_active = False  # 软删除
                        db.commit()
                        
                        # 刷新显示
                        self._refresh_directories()
                        QMessageBox.information(self, "成功", "目录已成功移除")
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