import configparser
import os
import sys

import cv2
import imutils
import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage, QColor, qRgb
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, \
    QHBoxLayout, QVBoxLayout, QComboBox, QSlider, QLayout, QSizePolicy
from CustomWorkerThread import Worker


class EditorWindow(QWidget):
    def __init__(self, img_path, app_id):
        super().__init__()

        # Inits

        self.app_id = app_id
        self.img_path = img_path

        # Declarations for image preview area
        self.original_image_lbl = None
        self.edited_image_lbl = None
        # Read in images
        self.original_cv_img = cv2.imread(self.img_path)
        self.edited_cv_img = cv2.imread(self.img_path)

        self.image_preview_layout = None

        # Declarations for editing grid area
        self.editor_grid = None
        self.filter_label = None
        self.filter_dropdown = None
        self.filters = ["None", "Sharpen", "Sepia"]
        self.curr_filter = None

        ### Declarations for filter kernels
        self.sepia_kernel = np.matrix(([[0.393, 0.769, 0.189],
                                      [0.349, 0.686, 0.168],
                                      [0.272, 0.534, 0.131]]))
        self.sharpen_kernel = np.matrix(([[-1, -1, -1],
                                        [-1, 9, -1],
                                        [-1, -1, -1]]))

        # Tracks Slider Values (Allows manipulation before running filters)
        # Will be used to export images
        self.brightness_lvl = 0
        self.contrast_lvl = 0

        # Declaration for btn area
        self.footer_hbox = None
        self.open_export_btn = None
        self.bulk_apply_btn = None
        self.cancel_btn = None

        # Main Layout Init
        self.main_layout = QVBoxLayout()

        # Builds main layout areas
        self.create_preview_layout()
        self.create_editing_area()
        self.create_footer_btn_area()

        # Set the main layout after everything is build
        self.setLayout(self.main_layout)
        # show call
        self.show()

    def show(self):
        # Can format main window here too
        super().show()

    def create_preview_layout(self):
        self.image_preview_layout = QHBoxLayout()

        self.original_image_lbl = QLabel()
        self.original_image_lbl.setPixmap(QPixmap(self.img_path))
        self.original_image_lbl.setPixmap(
            QPixmap((self.img_path)).scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.original_image_lbl.setScaledContents(False)
        self.image_preview_layout.addWidget(self.original_image_lbl)

        self.edited_image_lbl = QLabel()
        self.edited_image_lbl.setPixmap(
            QPixmap(self.img_path).scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.edited_image_lbl.setScaledContents(False)
        self.image_preview_layout.addWidget((self.edited_image_lbl))

        self.main_layout.addLayout(self.image_preview_layout)

    def create_editing_area(self):
        self.editor_grid = QGridLayout()
        self.editor_grid.setSpacing(10)

        # Create filter area and add to editor grid
        self.filter_label = QLabel("Filters")
        self.filter_label.setStyleSheet('color: white')
        # Dropdown Setup
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(self.filters)
        self.filter_dropdown.textActivated.connect(self.on_filter_changed)

        self.editor_grid.addWidget(self.filter_label, 0, 0)
        self.editor_grid.addWidget(self.filter_dropdown, 0, 1)

        # Set up Brightness Editor and add to grid
        self.bright_label = QLabel("Brightness")
        self.bright_label.setStyleSheet('color: white')

        self.bright_slider = QSlider(Qt.Horizontal)
        self.bright_slider.setValue(25)
        self.bright_slider.valueChanged['int'].connect(self.on_brightness_changed)

        self.editor_grid.addWidget(self.bright_label, 1, 0)
        self.editor_grid.addWidget(self.bright_slider, 1, 1)

        # Set up Contrast Editor and add to grid
        self.con_label = QLabel("Contrast")
        self.con_label.setStyleSheet('color: white')

        self.con_slider = QSlider(Qt.Horizontal)
        self.con_slider.setRange(1, 100)
        self.con_slider.setValue(50)
        self.con_slider.sliderReleased.connect(self.set_contrast_levels)

        self.editor_grid.addWidget(self.con_label, 2, 0)
        self.editor_grid.addWidget(self.con_slider, 2, 1)

    def create_footer_btn_area(self):
        self.footer_hbox = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.footer_hbox.addWidget(self.cancel_btn)

        self.open_export_btn = QPushButton("Export")
        self.open_export_btn.clicked.connect(lambda: self.on_export(self.img_path))
        self.footer_hbox.addWidget(self.open_export_btn)
        self.bulk_apply_btn = QPushButton("Bulk Apply")
        self.bulk_apply_btn.clicked.connect(self.on_bulk_apply)
        self.footer_hbox.addWidget(self.bulk_apply_btn)

        self.main_layout.addLayout(self.footer_hbox)

        self.main_layout.addLayout(self.editor_grid)

    def set_label(self, cv2_img, label):
        """ This function will take image input and resize it
            only for display purpose and convert it to QImage
            to set at the label.
        """
        self.tmp = cv2_img
        cv2_img = imutils.resize(cv2_img, width=600)
        frame = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        q_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(q_image))

    def on_filter_changed(self):
        if self.curr_filter == self.filter_dropdown.currentText():
            self.curr_filter = None
        self.curr_filter = self.filter_dropdown.currentText()
        self.update_changes()

    def set_filter(self, filter):
        # Convert to proper forma, use numpy
        img = cv2.cvtColor(self.edited_cv_img, cv2.COLOR_BGR2RGB)
        img = np.array(img, dtype=np.float64)


        # Simply determine which filter to use
        if filter == "Sepia":
            img = cv2.transform(img, self.sepia_kernel)
        elif filter == "Sharpen":
            img = cv2.filter2D(self.edited_cv_img, -1, self.sharpen_kernel)
        elif filter == "None":
            img = self.original_cv_img

        # Clip Values and convert back to uint8 format for cv
        # Also, convert back from RGB to BGR
        img[np.where(img > 255)] = 255
        img = np.array(img, dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    def set_brightness_levels(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, self.brightness_lvl)
        v[v > 255] = 255
        v[v < 0] = 0
        final_hsv = cv2.merge((h, s, v))
        back_to_bgr = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return back_to_bgr

    def on_brightness_changed(self, new_val):
        # Limit the brightness value a bit
        # brightness > 25 = brighten, brightness < 25 = darken
        self.brightness_lvl = new_val - 25
        self.update_changes()

    def set_contrast_levels(self):
        pass

    def on_contrast_changed(self, new_val):
        pass

    def update_changes(self):
        # This method should iterate over ALL changes and apply them. Maybe only apply them if they've been updated?
        img = self.edited_cv_img
        if self.curr_filter is not None:
            img = self.set_filter(self.curr_filter)
        img = self.set_brightness_levels(img=img)
        self.set_label(img, self.edited_image_lbl)

    def on_export_clicked(self):
        pass

    def on_export(self, img_path):
        # Here load the cv2 img again and rerun all current values on it.
        # TODO: Allow user to choose file path. Do this HERE IN THE EDITOR UI
        # Do NOT create a separate file or class. Make widget and show it.

        final_img = cv2.imread(img_path)
        print("Exported Image")
        if self.curr_filter is not None:
            final_img = self.set_filter(self.curr_filter)
        final_img = self.set_brightness_levels(final_img)

        if not os.path.exists("cache/test"):
            os.mkdir("cache/test")

        cv2.imwrite("cache/test/test_img.jpg", final_img)

    def on_bulk_apply(self):
        screenshot_dir = str(os.path.dirname(self.img_path))
        for x in os.listdir(screenshot_dir):
            print(x)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow(
        img_path="C:/Program Files (x86)/Steam/userdata/100834795/760/remote//1061910/screenshots/20220917154717_1.jpg",
        app_id=100834795)
    app.exec_()
