import sys

import cv2
import imutils
import numpy as np
import skimage.exposure
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QImage, QColor, qRgb
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, \
    QHBoxLayout, QVBoxLayout, QComboBox, QSlider


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
        self.filters = ["Red", "Green", "Blue", "Sepia", "Vintage"]
        self.curr_filter = None

        ### Declarations for filter kernels
        self.sepia_kernel = np.array(([0.272, 0.534, 0.131],
                                      [0.349, 0.686, 0.168],
                                      [0.393, 0.769, 0.189]))
        self.sharpen_kernel = np.array(([-1, -1, -1],
                                        [-1, 9, -1],
                                        [-1, -1, -1]))

        # Tracks Slider Values (Allows manipulation before running filters)
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
        self.setFixedSize(1000, 400)
        super().show()

    def create_preview_layout(self):
        self.image_preview_layout = QHBoxLayout()

        self.original_image_lbl = QLabel()
        self.original_image_lbl.setPixmap(QPixmap(self.img_path))
        self.original_image_lbl.setPixmap(
            QPixmap((self.img_path)).scaled(500, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.original_image_lbl.setScaledContents(False)
        self.image_preview_layout.addWidget(self.original_image_lbl)

        self.edited_image_lbl = QLabel()
        self.edited_image_lbl.setPixmap(
            QPixmap(self.img_path).scaled(500, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.edited_image_lbl.setScaledContents(False)
        self.image_preview_layout.addWidget((self.edited_image_lbl))

        self.main_layout.addLayout(self.image_preview_layout)

    def create_editing_area(self):
        self.editor_grid = QGridLayout()
        self.editor_grid.setSpacing(10)

        # Create filter area and add to editor grid
        self.filter_label = QLabel("Filters")
        # Dropdown Setup
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(self.filters)
        self.filter_dropdown.textActivated.connect(self.on_filter_changed)

        self.editor_grid.addWidget(self.filter_label, 0, 0)
        self.editor_grid.addWidget(self.filter_dropdown, 0, 1)

        # Set up Brightness Editor and add to grid
        self.bright_label = QLabel("Brightness")

        self.bright_slider = QSlider(Qt.Horizontal)
        self.bright_slider.setValue(25)
        self.bright_slider.valueChanged['int'].connect(self.on_brightness_changed)

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

    def set_label(self, cv2_img, label):
        """ This function will take image input and resize it
            only for display purpose and convert it to QImage
            to set at the label.
        """
        self.tmp = cv2_img
        cv2_img = imutils.resize(cv2_img, width=500)
        frame = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        q_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(q_image))

    def on_filter_changed(self):
        self.curr_filter = self.filter_dropdown.currentText()
        self.update_changes()

    def set_filter(self, filter):
        if filter == "Sepia":
            return cv2.filter2D(self.edited_cv_img, kernel=self.sepia_kernel)

    def set_brightness_levels(self):
        hsv = cv2.cvtColor(self.edited_cv_img, cv2.COLOR_BGR2HSV)
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
        img = self.set_brightness_levels()
        self.set_label(img, self.edited_image_lbl)

    def on_export(self):
        # Here load the cv2 img again and rerun all current values on it.
        final_img = cv2.imread(self.img_path, cv2.COLOR_RGB)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow(
        img_path="C:/Program Files (x86)/Steam/userdata/100834795/760/remote//1061910/screenshots/20220917154717_1.jpg",
        app_id=100834795)
    app.exec_()
