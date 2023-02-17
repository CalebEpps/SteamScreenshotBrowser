import os
import sys
import traceback
import urllib.request
from functools import partial

from PySide2.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, \
    QScrollArea, QHBoxLayout, QProgressBar, QProgressDialog, QVBoxLayout, QSizePolicy

from SteamAppAPI import SteamApp


class MyLabel(QLabel):
    def __init__(self):
        super().__init__()


# Thanks to pythonguis.com for this multi-threaded modular solution!
class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    # Use progress to update based on number of games loaded already
    progress = Signal(int)
    result = Signal(object)


class Worker(QRunnable, QObject):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.running_function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress'] = self.signals.progress

    @Slot()
    def run(self):
        try:
            print("Try")
            result = self.running_function(*self.args, **self.kwargs)
        except NotImplementedError:
            print("error")
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            print("else")
            self.signals.result.emit(result)
        finally:
            print("Finally")
            self.signals.finished.emit()


# It creates a window with a scrollable grid of images.
class ScreenshotBrowser(QMainWindow):

    def __init__(self, steam_user_id):
        super().__init__()
        # Declarations
        self.title_label = None
        self.scroll_area = None
        self.worker = None
        self.threadpool = None
        self.labels = None

        self.home_grid = None
        self.game_grid = None
        # Widgets holds scroll area (assigned in render_ui())
        self.main_widget = QWidget()
        self.loading_box = QProgressDialog()
        self.loading_bar = QProgressBar()
        self.counter_test = 0
        self.steam_user_id = str(steam_user_id)
        self.steam_screenshot_path = f"C:/Program Files (x86)/Steam/userdata/{self.steam_user_id}/760/remote/"
        self.titles = self.get_app_ids_from_screenshot_folder()
        print(self.titles)

        # Main Window Attributes
        self.setWindowTitle("Sing's Screenshot Browser")
        self.setMinimumSize(1280,720)
        # Makes the background look better
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)

        # Start Loading Box
        self.loading_box_populator()

        self.threadpool = QThreadPool()
        self.start_labels_thread()
        # print(f"Grid Item Count: {str(self.grid.count())}")

    def loading_complete(self):
        self.loading_box.close()
        self.render_ui()

    def label_clicked(self, img_path, event):
        print("Label Clicked")
        index = self.labels.index(img_path)
        print(self.titles[index])
        print(img_path)

        for x in reversed(range(self.home_grid.count())):
            widget = self.home_grid.itemAt(x).widget()
            widget.setParent(None)
            widget.deleteLater()
        try:
            self.build_game_grid(self.titles[index])
        except IndexError:
            pass



    def back_btn_clicked(self):
        for x in reversed(range(self.home_grid.count())):
            widget = self.home_grid.itemAt(x).widget()
            widget.setParent(None)
            widget.deleteLater()
        try:
            self.build_home_grid()
        except IndexError:
            pass

    def start_labels_thread(self):
        self.worker = Worker(function=self.get_image_paths)
        self.worker.signals.finished.connect(self.loading_complete)
        self.worker.signals.result.connect(self.set_labels)
        self.worker.signals.progress.connect(self.set_progress_bar)
        self.threadpool.globalInstance().start(self.worker)

    def loading_box_populator(self):
        self.loading_box.setLabelText("Loading, please wait.")
        self.loading_box.setBar(self.loading_bar)
        self.loading_box.setMinimum(0)
        self.loading_box.setMaximum(len(self.get_app_ids_from_screenshot_folder()))
        self.loading_box.show()

    def set_labels(self, labels):
        self.labels = labels

    def set_progress_bar(self, value):
        self.loading_box.setValue(value)
    def render_ui(self):
        # Defining the UI Elements and their layouts

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        # Title label Init
        self.title_label = QLabel("Sing's Screenshot Browser")
        self.title_label.setAlignment(Qt.AlignCenter)
        hbox.addWidget(self.title_label)

        # Q. Button Init
        quit_btn = QPushButton("Quit")
        # quit_btn.clicked.connect(self.close())
        hbox.addWidget(quit_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_btn_clicked)
        hbox.addWidget(back_btn)

        # Scroll Area Init
        scroll_area = QScrollArea()

        # Widget that holds the scroll area
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVisible(True)
        scroll_area.setEnabled(True)
        # Creation of image grid
        self.home_grid = QGridLayout()
        self.home_grid.setVerticalSpacing(10)
        self.home_grid.setContentsMargins(10, 10, 10, 10)

        # Loop that adds returned values from different thread to the grid layout
        self.build_home_grid()

        #TODO: here add a nested loop that builds the ENTIRE thing from render_ui() again, including a widget that can be set as central. Then try to replace the ENTIRE thing.
        #If that doesn't work, then making everything class scoped and use the method you are now

        print("Grid items after loop: ", self.home_grid.count())
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_widget.setLayout(self.home_grid)

        # Kinda like a parenting thing. Adds widget to grid, and sets the box to the main layout
        print(vbox.sizeConstraint())
        vbox.addLayout(hbox)
        vbox.addWidget(scroll_area)
        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)
        self.show()

    def show(self):
        super().show()

    def get_image_paths(self, progress):
        img_paths = []
        counter = 0
        for x in self.get_app_ids_from_screenshot_folder():
            counter += 1
            steam_api = SteamApp(x)
            img_path = self.load_pixmap_for_home(steam_api)
            img_paths.append(img_path)

            progress.emit(counter)

        return img_paths

    def build_game_grid(self, app_id):
        screenshot_paths = self.load_screenshots_for_game(str(app_id))
        row, col = 0, 0
        for x in screenshot_paths:
            label = QLabel()
            pixmap = QPixmap(x)
            label.setScaledContents(True)
            label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.home_grid.addWidget(label, row, col)
            col += 1
            if col == 4:
                row += 1
                col = 0

    def build_home_grid(self):
        row, col, curr_item = 0, 0, 0
        for x in self.labels:
            label = QLabel()
            pixmap = QPixmap(x)
            label.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setScaledContents(True)
            label.setContentsMargins(5, 5, 5, 5)
            label.mousePressEvent = partial(self.label_clicked, self.labels[curr_item])
            self.home_grid.addWidget(label, row, col)
            col += 1
            curr_item += 1
            if col == 4:
                row += 1
                col = 0


    @staticmethod
    def load_pixmap_for_home(steam_api):
        img_path = "cache/image_cache/" + steam_api.get("name").replace(":", "") + "_header.jpg"
        if not os.path.exists(img_path):
            header_link = steam_api.get("header_image")
            urllib.request.urlretrieve(header_link, img_path)
            print(img_path)
        return img_path



    # Loads screenshot links from directory based on app id
    def load_screenshots_for_game(self, app_id):
        """
        It takes a Steam directory and an app_id, and returns a list of paths to all the screenshots for that game

        param app_id: The Steam App ID of the game you want to get the screenshots for
        :return: A list of paths to the screenshots for a given game.
        """
        paths_list = []
        full_path = f"{self.steam_screenshot_path}/{app_id}/screenshots"
        for file in os.listdir(full_path):
            file_path = f"{full_path}/{file}"
            paths_list.append(file_path)

        return paths_list

    def get_app_ids_from_screenshot_folder(self):
        return list(os.listdir(self.steam_screenshot_path))

    def label_hover_begin(self, label, img_path):
        index = self.labels.index(img_path)
        label.setText(self.titles[index])

    def label_hover_end(self, img_path):
        pass

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
        for i in range(self.home_grid.count()):
            item = self.home_grid.itemAt(i)
            widget = item.widget()
            pixmap = widget.pixmap()
            height = pixmap.height()
            if height != 0:
                aspect_ratio = max(aspect_ratio, pixmap.width() / height)

        for x in range(self.home_grid.count()):
            cell = self.home_grid.itemAt(x)
            cell.widget().setFixedSize(size)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotBrowser(steam_user_id=100834795)
    app.exec_()
