# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1024, 768)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.left_sidebar = QWidget(self.centralwidget)
        self.left_sidebar.setObjectName(u"left_sidebar")
        self.left_sidebar.setMinimumSize(QSize(240, 0))
        self.left_sidebar.setMaximumSize(QSize(280, 16777215))
        self.left_sidebar.setStyleSheet(u"background-color: #2c3e50; color: #ecf0f1;")
        self.verticalLayout_2 = QVBoxLayout(self.left_sidebar)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_title = QLabel(self.left_sidebar)
        self.label_title.setObjectName(u"label_title")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_title.setStyleSheet(u"color: #3498db; padding: 10px;")

        self.verticalLayout_2.addWidget(self.label_title)

        self.listWidget_main_nav = QListWidget(self.left_sidebar)
        icon = QIcon()
        icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qlistwidgetitem = QListWidgetItem(self.listWidget_main_nav)
        __qlistwidgetitem.setIcon(icon);
        __qlistwidgetitem1 = QListWidgetItem(self.listWidget_main_nav)
        __qlistwidgetitem1.setIcon(icon);
        __qlistwidgetitem2 = QListWidgetItem(self.listWidget_main_nav)
        __qlistwidgetitem2.setIcon(icon);
        self.listWidget_main_nav.setObjectName(u"listWidget_main_nav")
        font1 = QFont()
        font1.setPointSize(12)
        self.listWidget_main_nav.setFont(font1)
        self.listWidget_main_nav.setIconSize(QSize(24, 24))
        self.listWidget_main_nav.setStyleSheet(u"\n"
"QListWidget {\n"
"    background-color: #34495e;\n"
"    border: none;\n"
"    outline: none;\n"
"}\n"
"QListWidget::item {\n"
"    color: #ecf0f1;\n"
"    padding: 12px 16px;\n"
"    border-bottom: 1px solid #2c3e50;\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: #3498db;\n"
"    color: white;\n"
"    border-left: 4px solid #2980b9;\n"
"}\n"
"QListWidget::item:hover {\n"
"    background-color: #3d566e;\n"
"}\n"
"          ")

        self.verticalLayout_2.addWidget(self.listWidget_main_nav)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_local_dir = QLabel(self.left_sidebar)
        self.label_local_dir.setObjectName(u"label_local_dir")
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.label_local_dir.setFont(font2)
        self.label_local_dir.setStyleSheet(u"color: #bdc3c7; padding: 5px;")

        self.horizontalLayout_3.addWidget(self.label_local_dir)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.add_dir = QToolButton(self.left_sidebar)
        self.add_dir.setObjectName(u"add_dir")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.add_dir.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.add_dir)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.tree_localdir = QTreeWidget(self.left_sidebar)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_localdir.setHeaderItem(__qtreewidgetitem)
        self.tree_localdir.setObjectName(u"tree_localdir")

        self.verticalLayout_2.addWidget(self.tree_localdir)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.pushButton_settings = QPushButton(self.left_sidebar)
        self.pushButton_settings.setObjectName(u"pushButton_settings")
        self.pushButton_settings.setFont(font1)
        self.pushButton_settings.setIcon(icon)
        self.pushButton_settings.setIconSize(QSize(20, 20))

        self.verticalLayout_2.addWidget(self.pushButton_settings)


        self.horizontalLayout.addWidget(self.left_sidebar)

        self.main_content = QWidget(self.centralwidget)
        self.main_content.setObjectName(u"main_content")
        self.verticalLayout = QVBoxLayout(self.main_content)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.header = QWidget(self.main_content)
        self.header.setObjectName(u"header")
        self.horizontalLayout_2 = QHBoxLayout(self.header)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_all_photos = QLabel(self.header)
        self.label_all_photos.setObjectName(u"label_all_photos")
        font3 = QFont()
        font3.setPointSize(16)
        font3.setBold(True)
        self.label_all_photos.setFont(font3)
        self.label_all_photos.setStyleSheet(u"color: #2c3e50; padding: 5px;")

        self.horizontalLayout_2.addWidget(self.label_all_photos)

        self.label_photo_count = QLabel(self.header)
        self.label_photo_count.setObjectName(u"label_photo_count")
        self.label_photo_count.setFont(font1)
        self.label_photo_count.setStyleSheet(u"color: #7f8c8d; padding: 5px;")

        self.horizontalLayout_2.addWidget(self.label_photo_count)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_refresh = QPushButton(self.header)
        self.pushButton_refresh.setObjectName(u"pushButton_refresh")
        self.pushButton_refresh.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.pushButton_refresh)


        self.verticalLayout.addWidget(self.header)

        self.thum_body = QListView(self.main_content)
        self.thum_body.setObjectName(u"thum_body")
        self.thum_body.setViewMode(QListView.ViewMode.IconMode)

        self.verticalLayout.addWidget(self.thum_body)

        self.exif_panel = QWidget(self.main_content)
        self.exif_panel.setObjectName(u"exif_panel")
        self.exif_panel.setMaximumSize(QSize(16777215, 280))
        self.horizontalLayout_4 = QHBoxLayout(self.exif_panel)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(15, 15, 15, 15)
        self.preview_container = QWidget(self.exif_panel)
        self.preview_container.setObjectName(u"preview_container")
        self.preview_container.setMinimumSize(QSize(200, 200))
        self.preview_container.setMaximumSize(QSize(200, 200))
        self.verticalLayout_4 = QVBoxLayout(self.preview_container)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.image_preview = QLabel(self.preview_container)
        self.image_preview.setObjectName(u"image_preview")
        self.image_preview.setMinimumSize(QSize(180, 120))
        self.image_preview.setMaximumSize(QSize(180, 120))
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.image_preview)

        self.label_basic_info = QLabel(self.preview_container)
        self.label_basic_info.setObjectName(u"label_basic_info")
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(True)
        self.label_basic_info.setFont(font4)

        self.verticalLayout_4.addWidget(self.label_basic_info)

        self.value_filename = QLabel(self.preview_container)
        self.value_filename.setObjectName(u"value_filename")
        font5 = QFont()
        font5.setPointSize(9)
        self.value_filename.setFont(font5)
        self.value_filename.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.value_filename)

        self.value_dimensions = QLabel(self.preview_container)
        self.value_dimensions.setObjectName(u"value_dimensions")
        self.value_dimensions.setFont(font5)

        self.verticalLayout_4.addWidget(self.value_dimensions)


        self.horizontalLayout_4.addWidget(self.preview_container)

        self.scrollArea_exif = QScrollArea(self.exif_panel)
        self.scrollArea_exif.setObjectName(u"scrollArea_exif")
        self.scrollArea_exif.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 532, 336))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setSpacing(15)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.camera_info_group = QWidget(self.scrollAreaWidgetContents)
        self.camera_info_group.setObjectName(u"camera_info_group")
        self.verticalLayout_6 = QVBoxLayout(self.camera_info_group)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.label_camera_info = QLabel(self.camera_info_group)
        self.label_camera_info.setObjectName(u"label_camera_info")
        font6 = QFont()
        font6.setPointSize(11)
        font6.setBold(True)
        self.label_camera_info.setFont(font6)

        self.verticalLayout_6.addWidget(self.label_camera_info)

        self.formLayout_camera = QFormLayout()
        self.formLayout_camera.setObjectName(u"formLayout_camera")
        self.formLayout_camera.setHorizontalSpacing(15)
        self.formLayout_camera.setVerticalSpacing(8)
        self.label_camera = QLabel(self.camera_info_group)
        self.label_camera.setObjectName(u"label_camera")
        self.label_camera.setFont(font5)

        self.formLayout_camera.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_camera)

        self.value_camera = QLabel(self.camera_info_group)
        self.value_camera.setObjectName(u"value_camera")
        self.value_camera.setFont(font5)

        self.formLayout_camera.setWidget(0, QFormLayout.ItemRole.FieldRole, self.value_camera)

        self.label_lens = QLabel(self.camera_info_group)
        self.label_lens.setObjectName(u"label_lens")
        self.label_lens.setFont(font5)

        self.formLayout_camera.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_lens)

        self.value_lens = QLabel(self.camera_info_group)
        self.value_lens.setObjectName(u"value_lens")
        self.value_lens.setFont(font5)

        self.formLayout_camera.setWidget(1, QFormLayout.ItemRole.FieldRole, self.value_lens)

        self.label_date = QLabel(self.camera_info_group)
        self.label_date.setObjectName(u"label_date")
        self.label_date.setFont(font5)

        self.formLayout_camera.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_date)

        self.value_date = QLabel(self.camera_info_group)
        self.value_date.setObjectName(u"value_date")
        self.value_date.setFont(font5)

        self.formLayout_camera.setWidget(2, QFormLayout.ItemRole.FieldRole, self.value_date)


        self.verticalLayout_6.addLayout(self.formLayout_camera)


        self.verticalLayout_5.addWidget(self.camera_info_group)

        self.exposure_info_group = QWidget(self.scrollAreaWidgetContents)
        self.exposure_info_group.setObjectName(u"exposure_info_group")
        self.verticalLayout_7 = QVBoxLayout(self.exposure_info_group)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(10, 10, 10, 10)
        self.label_exposure_info = QLabel(self.exposure_info_group)
        self.label_exposure_info.setObjectName(u"label_exposure_info")
        self.label_exposure_info.setFont(font6)

        self.verticalLayout_7.addWidget(self.label_exposure_info)

        self.formLayout_exposure = QFormLayout()
        self.formLayout_exposure.setObjectName(u"formLayout_exposure")
        self.formLayout_exposure.setHorizontalSpacing(15)
        self.formLayout_exposure.setVerticalSpacing(8)
        self.label_aperture = QLabel(self.exposure_info_group)
        self.label_aperture.setObjectName(u"label_aperture")
        self.label_aperture.setFont(font5)

        self.formLayout_exposure.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_aperture)

        self.value_aperture = QLabel(self.exposure_info_group)
        self.value_aperture.setObjectName(u"value_aperture")
        self.value_aperture.setFont(font5)

        self.formLayout_exposure.setWidget(0, QFormLayout.ItemRole.FieldRole, self.value_aperture)

        self.label_shutter = QLabel(self.exposure_info_group)
        self.label_shutter.setObjectName(u"label_shutter")
        self.label_shutter.setFont(font5)

        self.formLayout_exposure.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_shutter)

        self.value_shutter = QLabel(self.exposure_info_group)
        self.value_shutter.setObjectName(u"value_shutter")
        self.value_shutter.setFont(font5)

        self.formLayout_exposure.setWidget(1, QFormLayout.ItemRole.FieldRole, self.value_shutter)

        self.label_iso = QLabel(self.exposure_info_group)
        self.label_iso.setObjectName(u"label_iso")
        self.label_iso.setFont(font5)

        self.formLayout_exposure.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_iso)

        self.value_iso = QLabel(self.exposure_info_group)
        self.value_iso.setObjectName(u"value_iso")
        self.value_iso.setFont(font5)

        self.formLayout_exposure.setWidget(2, QFormLayout.ItemRole.FieldRole, self.value_iso)

        self.label_focal = QLabel(self.exposure_info_group)
        self.label_focal.setObjectName(u"label_focal")
        self.label_focal.setFont(font5)

        self.formLayout_exposure.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_focal)

        self.value_focal = QLabel(self.exposure_info_group)
        self.value_focal.setObjectName(u"value_focal")
        self.value_focal.setFont(font5)

        self.formLayout_exposure.setWidget(3, QFormLayout.ItemRole.FieldRole, self.value_focal)


        self.verticalLayout_7.addLayout(self.formLayout_exposure)


        self.verticalLayout_5.addWidget(self.exposure_info_group)

        self.other_info_group = QWidget(self.scrollAreaWidgetContents)
        self.other_info_group.setObjectName(u"other_info_group")
        self.verticalLayout_8 = QVBoxLayout(self.other_info_group)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(10, 10, 10, 10)
        self.label_other_info = QLabel(self.other_info_group)
        self.label_other_info.setObjectName(u"label_other_info")
        self.label_other_info.setFont(font6)

        self.verticalLayout_8.addWidget(self.label_other_info)

        self.formLayout_other = QFormLayout()
        self.formLayout_other.setObjectName(u"formLayout_other")
        self.formLayout_other.setHorizontalSpacing(15)
        self.formLayout_other.setVerticalSpacing(8)
        self.label_gps = QLabel(self.other_info_group)
        self.label_gps.setObjectName(u"label_gps")
        self.label_gps.setFont(font5)

        self.formLayout_other.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_gps)

        self.value_gps = QLabel(self.other_info_group)
        self.value_gps.setObjectName(u"value_gps")
        self.value_gps.setFont(font5)

        self.formLayout_other.setWidget(0, QFormLayout.ItemRole.FieldRole, self.value_gps)

        self.label_copyright = QLabel(self.other_info_group)
        self.label_copyright.setObjectName(u"label_copyright")
        self.label_copyright.setFont(font5)

        self.formLayout_other.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_copyright)

        self.value_copyright = QLabel(self.other_info_group)
        self.value_copyright.setObjectName(u"value_copyright")
        self.value_copyright.setFont(font5)

        self.formLayout_other.setWidget(1, QFormLayout.ItemRole.FieldRole, self.value_copyright)


        self.verticalLayout_8.addLayout(self.formLayout_other)


        self.verticalLayout_5.addWidget(self.other_info_group)

        self.scrollArea_exif.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_4.addWidget(self.scrollArea_exif)


        self.verticalLayout.addWidget(self.exif_panel)


        self.horizontalLayout.addWidget(self.main_content)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u7ba1\u7406\u5668", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow", u"\u7167\u7247\u7ba1\u7406\u5668", None))

        __sortingEnabled = self.listWidget_main_nav.isSortingEnabled()
        self.listWidget_main_nav.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget_main_nav.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u5168\u90e8\u7167\u7247", None));
        ___qlistwidgetitem1 = self.listWidget_main_nav.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u6536\u85cf\u5939", None));
        ___qlistwidgetitem2 = self.listWidget_main_nav.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u76f8\u518c", None));
        self.listWidget_main_nav.setSortingEnabled(__sortingEnabled)

        self.label_local_dir.setText(QCoreApplication.translate("MainWindow", u"\u672c\u5730\u76ee\u5f55", None))
        self.add_dir.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_settings.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.label_all_photos.setText(QCoreApplication.translate("MainWindow", u"\u5168\u90e8\u7167\u7247", None))
        self.label_photo_count.setText(QCoreApplication.translate("MainWindow", u"60 \u5f20\u7167\u7247", None))
        self.pushButton_refresh.setText("")
        self.image_preview.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u9884\u89c8", None))
        self.label_basic_info.setText(QCoreApplication.translate("MainWindow", u"\u57fa\u672c\u4fe1\u606f", None))
        self.value_filename.setText(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6\u540d: -", None))
        self.value_dimensions.setText(QCoreApplication.translate("MainWindow", u"\u5c3a\u5bf8: -", None))
        self.label_camera_info.setText(QCoreApplication.translate("MainWindow", u"\u76f8\u673a\u4fe1\u606f", None))
        self.label_camera.setText(QCoreApplication.translate("MainWindow", u"\u76f8\u673a\u578b\u53f7\uff1a", None))
        self.value_camera.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_lens.setText(QCoreApplication.translate("MainWindow", u"\u955c\u5934\uff1a", None))
        self.value_lens.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_date.setText(QCoreApplication.translate("MainWindow", u"\u62cd\u6444\u65f6\u95f4\uff1a", None))
        self.value_date.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_exposure_info.setText(QCoreApplication.translate("MainWindow", u"\u66dd\u5149\u53c2\u6570", None))
        self.label_aperture.setText(QCoreApplication.translate("MainWindow", u"\u5149\u5708\uff1a", None))
        self.value_aperture.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_shutter.setText(QCoreApplication.translate("MainWindow", u"\u5feb\u95e8\u901f\u5ea6\uff1a", None))
        self.value_shutter.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_iso.setText(QCoreApplication.translate("MainWindow", u"ISO\uff1a", None))
        self.value_iso.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_focal.setText(QCoreApplication.translate("MainWindow", u"\u7126\u8ddd\uff1a", None))
        self.value_focal.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_other_info.setText(QCoreApplication.translate("MainWindow", u"\u5176\u4ed6\u4fe1\u606f", None))
        self.label_gps.setText(QCoreApplication.translate("MainWindow", u"GPS\u5750\u6807\uff1a", None))
        self.value_gps.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.label_copyright.setText(QCoreApplication.translate("MainWindow", u"\u7248\u6743\u4fe1\u606f\uff1a", None))
        self.value_copyright.setText(QCoreApplication.translate("MainWindow", u"-", None))
    # retranslateUi

