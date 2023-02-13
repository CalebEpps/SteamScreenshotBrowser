import os
import sys
import urllib.request

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, \
    QScrollArea, QHBoxLayout, QProgressDialog
import threading

from SteamAppAPI import SteamApp


# It creates a window with a scrollable grid of images.
class ScreenshotBrowser(QMainWindow):

    def __init__(self, steam_user_id):
        self.grid = None
        self.steam_user_id = str(steam_user_id)
        self.steam_screenshot_path = "C:/Program Files (x86)/Steam/userdata/" + self.steam_user_id + "/760/remote/"
        super().__init__()

        self.setWindowTitle("Sing's Screenshot Browser")
        self.setMinimumSize(1920, 1080)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)




        self.render_ui()
        self.show()



    def render_ui(self):
        # Defining the UI Elements and their layouts
        hbox = QHBoxLayout()

        # Title label Init
        title_label = QLabel("Sing's Screenshot Browser")
        title_label.setAlignment(Qt.AlignCenter)
        hbox.addWidget(title_label)

        # Q. Button Init
        quit_btn = QPushButton("Quit")
        # quit_btn.clicked.connect(self.close())
        hbox.addWidget(quit_btn)

        # Scroll Area Init
        scroll_area = QScrollArea()
        self.setCentralWidget(scroll_area)

        # Widget that holds the scroll area
        widget = QWidget()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)

        # Creation of image grid
        self.grid = QGridLayout(widget)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.build_home_grid()


        # Kinda like a parenting thing. Adds widget to grid, and sets the box to the main layout
        widget.setLayout(self.grid)
        self.setLayout(hbox)

    def show(self):
        super().show()

    def build_home_grid(self):
        row, col = 0, 0
        for x in self.get_app_ids_from_screenshot_folder():
            steam_api = SteamApp(x)
            label = QLabel()
            pixmap = QPixmap(self.load_pixmap_for_home(steam_api))
            label.setPixmap(pixmap.scaled(600, 338, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setScaledContents(True)
            label.setMaximumSize(300, 100)
            label.setMinimumSize(100, 100)
            label.setContentsMargins(5, 5, 5, 5)
            self.grid.addWidget(label, row, col)
            col += 1
            if col == 5:
                row += 1
                col = 0

    def load_pixmap_for_home(self, steam_api):
        img_path = "cache/image_cache/" + str(steam_api.get("name").replace(":", "")) + "_header.jpg"
        if not os.path.exists(img_path):
            header_link = steam_api.get("header_image")
            urllib.request.urlretrieve(header_link, img_path)
            print(img_path)
        return img_path



    def build_game_grid(self, app_id):
        screenshot_paths = self.load_screenshots_for_game(str(app_id))
        row, col = 0, 0
        for x in screenshot_paths:
            label = QLabel()
            pixmap = QPixmap(x)
            label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setScaledContents(True)
            label.setMaximumSize(100, 100)
            label.setMinimumSize(100, 100)
            label.setContentsMargins(5, 5, 5, 5)
            self.grid.addWidget(label, row, col)
            col += 1
            if col == 5:
                row += 1
                col = 0

    # Loads screenshot links from directory based on app id
    def load_screenshots_for_game(self, app_id):
        """
        It takes a Steam directory and an app_id, and returns a list of paths to all the screenshots for that game

        :param steam_dir: The path to your Steam directory
        :param app_id: The Steam App ID of the game you want to get the screenshots for
        :return: A list of paths to the screenshots for a given game.
        """
        paths_list = []
        full_path = self.steam_screenshot_path + "/" + app_id + "/screenshots"
        for file in os.listdir(full_path):
            file_path = full_path + "/" + file
            paths_list.append(file_path)

        return paths_list

    def get_app_ids_from_screenshot_folder(self):
        app_ids = []
        for x in os.listdir(self.steam_screenshot_path):
            app_ids.append(x)
        return app_ids

    # Layout resize event
    def resizeEvent(self, event):
        """
        It sets the maximum size of each widget in the grid layout to be 1/5 of the size of the central widget, minus 20
        pixels for the border, minus 10 pixels for the spacing, minus 10 pixels for the margin

        :param event: The event object that was passed to the event handler
        """
        size = self.centralWidget().size()
        size -= QSize(20, 20)
        size /= 5
        size -= QSize(10, 10)
        size -= QSize(10, 10)

        # Calculate the maximum aspect ratio
        aspect_ratio = 0
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            widget = item.widget()
            pixmap = widget.pixmap()
            height = pixmap.height()
            if height != 0:
                aspect_ratio = max(aspect_ratio, pixmap.width() / height)

        for x in range(self.grid.count()):
            cell = self.grid.itemAt(x)
            cell.widget().setFixedSize(size)


class TestClass:
    def __init__(self):
        print("Initialized")

    def get_app_ids_from_screenshot_folder(self, steam_user_id, steam_screenshot_dir):
        app_ids = []
        for x in os.listdir(steam_screenshot_dir):
            app_ids.append(x)
        return app_ids


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotBrowser(steam_user_id=100834795)
    app.exec_()