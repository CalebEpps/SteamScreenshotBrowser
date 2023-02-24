import os
from MainWindow import ScreenshotBrowser
from Installer import Installer
from configparser import ConfigParser
import os
import sys
import urllib.request
from functools import partial

from PySide2.QtCore import QSize, Qt
from PySide2.QtCore import QThreadPool
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, \
    QScrollArea, QHBoxLayout, QProgressBar, QProgressDialog, QVBoxLayout, QSizePolicy

from CustomWorkerThread import Worker
from EditorWindow import EditorWindow
from SteamAppAPI import SteamApp

if __name__ == "__main__":

    if os.path.exists('cache/steam_info.config'):
        parser = ConfigParser()
        parser.read('cache/steam_info.config')
        print(parser['INFO']['path'])
        steam_path = parser['INFO']['path']
        app = QApplication(sys.argv)
        main_window = ScreenshotBrowser(steam_path)
    else:
        app = QApplication(sys.argv)
        installer = Installer()

    app.exec_()


