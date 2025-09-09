import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from qt_material import apply_stylesheet

def main():
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 加载UI文件
    ui_file = QFile("main.ui")
    ui_file.open(QIODevice.ReadOnly)
    
    # 使用QUiLoader加载UI
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    
    # 应用Material主题
    apply_stylesheet(app, theme='dark_blue.xml')
    
    # 设置窗口属性
    window.setWindowTitle("图片管理器 - Material Design")
    window.resize(1200, 800)
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
