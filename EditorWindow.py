import os
import sys
import traceback
import urllib.request
from functools import partial

from PySide2.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool, QPoint
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QPixmap, QImage, QColor, qRgb, qRed, qBlue, qGreen
from PySide2.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, \
    QScrollArea, QHBoxLayout, QProgressBar, QProgressDialog, QVBoxLayout, QSizePolicy, QComboBox, QSlider
from PIL import Image

from SteamAppAPI import SteamApp


class EditorWindow(QWidget):
    def __init__(self, img_path, app_id):
        super().__init__()

        # Inits

        self.app_id = app_id
        self.img_path = img_path
        # Declarations for image preview area
        self.original_image = None
        self.edited_image = None
        self.opened_img = QImage(self.img_path).scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.edited = QImage(self.img_path).scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_preview_layout = None
        # Declarations for editing grid area
        self.editor_grid = None
        self.filter_label = None
        self.filter_dropdown = None
        self.filters = ["Red", "Green", "Blue", "Sepia", "Vintage"]

        # Declaration for btn area
        self.footer_hbox = None

        # Main Layout Init
        self.main_layout = QVBoxLayout()

        # Builds image preview area, adds it to main layout
        self.create_preview_layout()
        self.create_editing_area()
        self.create_footer_btn_area()

        # Set the main layout after everything is build
        self.setLayout(self.main_layout)
        # show call
        self.show()

    def show(self):
        self.setFixedSize(1000, 400)
        super().show()

    def create_preview_layout(self):
        self.image_preview_layout = QHBoxLayout()

        self.original_image = QLabel()
        self.original_image.setPixmap(QPixmap(self.img_path))
        self.original_image.setPixmap(
            QPixmap((self.img_path)).scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.original_image.setScaledContents(False)
        self.image_preview_layout.addWidget(self.original_image)

        self.edited_image = QLabel()
        self.edited_image.setPixmap(
            QPixmap(self.img_path).scaled(500, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.edited_image.setScaledContents(False)
        self.image_preview_layout.addWidget((self.edited_image))

        self.main_layout.addLayout(self.image_preview_layout)

    def create_editing_area(self):
        self.editor_grid = QGridLayout()
        self.editor_grid.setSpacing(10)

        # Create filter area and add to editor grid
        self.filter_label = QLabel("Filters")
        # Dropdown Setup
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(self.filters)
        self.filter_dropdown.textActivated.connect(self.set_edited_photo_filter)

        self.editor_grid.addWidget(self.filter_label, 0, 0)
        self.editor_grid.addWidget(self.filter_dropdown, 0, 1)

        # Set up Brightness Editor and add to grid
        self.bright_label = QLabel("Brightness")

        self.bright_slider = QSlider(Qt.Horizontal)
        self.bright_slider.setRange(1, 100)
        self.bright_slider.setValue(50)
        self.bright_slider.sliderReleased.connect(self.set_brightness_levels)

        self.editor_grid.addWidget(self.bright_label, 1, 0)
        self.editor_grid.addWidget(self.bright_slider, 1, 1)

        # Set up Contrast Editor and add to grid
        self.con_label = QLabel("Contrast")

        self.con_slider = QSlider(Qt.Horizontal)
        self.con_slider.setRange(1, 100)
        self.con_slider.setValue(50)
        self.con_slider.sliderReleased.connect(self.set_contrast_levels)

        self.editor_grid.addWidget(self.con_label, 2, 0)
        self.editor_grid.addWidget(self.con_slider, 2, 1)

    def set_edited_photo_filter(self):
        selected_filter = self.filter_dropdown.currentText()
        if selected_filter == "Sepia":
            self.set_sepia()

    def set_sepia(self):
        width = self.edited.width()
        height = self.edited.height()
        new_image = self.edited.copy()
        print(new_image.pixelFormat())
        for x in range(width):
            for y in range(height):
                # Creates new RGB value for sepia filter
                rgb = QColor(new_image.pixelColor(x, y))
                r = min(255, int(rgb.red() * .393) + int(rgb.green() * .769) + int(rgb.blue() * .189))
                g = min(255, int(rgb.red() * .349) + int(rgb.green() * .686) + int(rgb.blue() * .168))
                b = min(255, int(rgb.red() * .272) + int(rgb.green() * .534) + int(rgb.blue() * .131))

                new_image.setPixel(x, y, qRgb(r, g, b))

        # new_image.save("test.jpg")
        new_pm = QPixmap().fromImage(new_image)
        self.edited = new_image.copy()

        self.edited_image.setPixmap(new_pm)

    def set_brightness_levels(self):
        width = self.edited.width()
        height = self.edited.height()
        new_image = self.edited.copy()

        for x in range(width):
            for y in range(height):
                # Creates new RGB value for sepia filter
                rgb = QColor(self.edited.pixelColor(x, y))
                r = min(255, rgb.red() * ((self.bright_slider.value() / 100) * 2))
                g = min(255, rgb.green() * ((self.bright_slider.value() / 100) * 2))
                b = min(255, rgb.blue() * ((self.bright_slider.value() / 100) * 2))

                new_image.setPixel(x, y, qRgb(r, g, b))

        # new_image.save("test.jpg")
        self.edited = new_image.copy()
        new_pm = QPixmap().fromImage(new_image)

        self.edited_image.setPixmap(new_pm)

    def set_contrast_levels(self):
        pass

    def create_footer_btn_area(self):
        self.footer_hbox = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.footer_hbox.addWidget(self.cancel_btn)

        self.open_export_btn = QPushButton("Export")
        self.footer_hbox.addWidget(self.open_export_btn)
        self.bulk_apply_btn = QPushButton("Bulk Apply")
        self.footer_hbox.addWidget(self.bulk_apply_btn)

        self.main_layout.addLayout(self.footer_hbox)

        self.main_layout.addLayout(self.editor_grid)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow(
        img_path="C:/Program Files (x86)/Steam/userdata/100834795/760/remote//1061910/screenshots/20220917154717_1.jpg",
        app_id=100834795)
    app.exec_()
