import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QPushButton, QToolButton
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 加载UI文件
        ui_file = QFile("main.ui")
        ui_file.open(QIODevice.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        # 设置中心部件
        self.setCentralWidget(self.ui)
        
        # 设置应用程序图标
        self.setWindowIcon(qta.icon('fa5s.images', color='#3498db'))
        self.setWindowTitle("📷 图片管理器")
        
        # 设置导航图标
        self.setup_navigation_icons()
        
        # 设置按钮图标
        self.setup_button_icons()
        
        # 设置窗口大小
        self.resize(1200, 800)
        
    def setup_navigation_icons(self):
        """设置导航列表的图标"""
        # 全部照片
        self.ui.listWidget_main_nav.item(0).setIcon(
            qta.icon('fa5s.image', color='#ecf0f1')
        )
        # 收藏夹
        self.ui.listWidget_main_nav.item(1).setIcon(
            qta.icon('fa5s.star', color='#ecf0f1')
        )
        # 相册
        self.ui.listWidget_main_nav.item(2).setIcon(
            qta.icon('fa5s.folder', color='#ecf0f1')
        )
    
    def setup_button_icons(self):
        """设置按钮图标"""
        # 添加目录按钮
        self.ui.add_dir.setIcon(
            qta.icon('fa5s.plus-circle', color='#3498db')
        )
        
        # 刷新按钮
        self.ui.pushButton_refresh.setIcon(
            qta.icon('fa5s.sync', color='#7f8c8d')
        )
        
        # 设置按钮
        self.ui.pushButton_settings.setIcon(
            qta.icon('fa5s.cog', color='#ecf0f1')
        )
        
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
        self.ui.pushButton_settings.setStyleSheet(settings_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
