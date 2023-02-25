import os
import sys
import urllib.request
from functools import partial

from PySide2.QtCore import QSize, Qt
from PySide2.QtCore import QThreadPool
from PySide2.QtGui import QPixmap, QImage, QFont
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, \
    QScrollArea, QHBoxLayout, QProgressBar, QProgressDialog, QVBoxLayout, QSizePolicy, QFileDialog

from CustomWorkerThread import Worker
from EditorWindow import EditorWindow
from SteamAppAPI import SteamApp
from MainWindow import ScreenshotBrowser
from configparser import ConfigParser


class Installer(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.path_layout = QHBoxLayout()

        self.title = QLabel("Sing's Screenshot Editor")
        self.title.setFont(QFont('Arial', 24))
        self.title.setAlignment(Qt.AlignCenter)

        self.select_path_inst_label = QLabel("Choose your Steam path")
        self.select_path_inst_label.setAlignment(Qt.AlignCenter)

        self.get_steam_path_btn = QPushButton("Choose")
        self.get_steam_path_btn.clicked.connect(self.on_select_steam_install_path_clicked)

        self.steam_path_label = QLabel()
        self.steam_path_label.setAlignment(Qt.AlignCenter)
        self.steam_path = None
        self.steam_id = None


        # Populate QHBox
        self.path_layout.addWidget(self.select_path_inst_label)
        self.path_layout.addWidget(self.steam_path_label)

        # Populate Main Layout
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.path_layout)
        self.main_layout.addWidget(self.get_steam_path_btn)
        self.setFixedSize(640, 480)
        self.setLayout(self.main_layout)
        self.show()

    def on_select_steam_install_path_clicked(self):
        self.steam_path = str(f"{QFileDialog.getExistingDirectory(self)}/userdata")
        self.steam_id = os.listdir(self.steam_path)[0]
        if self.steam_id == "0":
            self.steam_id = os.listdir(self.steam_path[1])
        print(self.steam_path)
        print(self.steam_id)


        if not os.path.exists("cache"):
            os.mkdir("cache")
            os.mkdir("cache/image_cache")

        parser = ConfigParser()
        parser["INFO"] = {
            "path": f"{self.steam_path}/{self.steam_id}",
            "export_path": "export/"
        }

        with open("cache/steam_info.config", 'w') as config:
            parser.write(config)


        self.close()

        main_program = ScreenshotBrowser(steam_path=f"{self.steam_path}/{self.steam_id}")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Installer()
    app.exec_()
