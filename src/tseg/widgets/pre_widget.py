from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from ..config import shared_config  # Import shared_config

from .prep import *

class PreProcessingWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QGridLayout(self)
        # self.setLayout(vbox)
        vbox = QVBoxLayout()
        self.ppGroupBox = QGroupBox("Pre-Processing", checkable=True)
        self.ppGroupBox.setLayout(vbox)
        layout.addWidget(self.ppGroupBox)

        self.ppGroupBox.clicked.connect(lambda: self._changed(self.ppGroupBox))
        # layout.addLayout(vbox, 0, 0)

        self.adap = QPushButton("adaptive thresh")
        self.sub_region = QSlider(Qt.Horizontal)
        self.sub_region.setMinimum(3)
        self.sub_region.setMaximum(100)
        self.sub_region.setValue(9)
        # self.sub_region.setPageStep(2)
        self.sub_region.setTickInterval(2)
        self.sub_region.setSingleStep(2)
        self.sub_region.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sub_region_lbl = QLabel("Sub region size: " + str(self.sub_region.value()) + "×" + str(self.sub_region.value()))
        # self.sub_region.valueChanged.connect(lambda: self._sub_region_changed(self.sub_region, self.sub_region_lbl))

        self.c_val_slider = QSlider(Qt.Horizontal)
        self.c_val_slider.setMinimum(1)
        self.c_val_slider.setMaximum(100)
        self.c_val_slider.setValue(5)
        self.c_val_lbl = QLabel("C Value: " + str(self.c_val_slider.value()))

        self.logTrans = QPushButton("Log transform")
        self.logTrans.clicked.connect(lambda: self._log_transform_clicked())

        vbox.addWidget(self.sub_region_lbl)
        vbox.addWidget(self.sub_region)
        vbox.addWidget(self.c_val_lbl)
        vbox.addWidget(self.c_val_slider)
        vbox.addWidget(self.adap)

        vbox.addWidget(self.logTrans)

        self.adap.clicked.connect(lambda: self.do_adaptive_thresh(self.viewer))

        def _sub_region_changed(slider, label):
            # Force the value to the nearest odd number
            value = slider.value()
            if value % 2 == 0:  # If even, adjust to the nearest odd
                value += 1 if value < slider.maximum() else -1
                slider.setValue(value)
            label.setText(f"Sub region size: {value}×{value}")
            shared_config["sub_region"] = self.sub_region.value()
            print(shared_config)

        self.sub_region.valueChanged.connect(lambda: _sub_region_changed(self.sub_region, self.sub_region_lbl))

        def _c_value_changed(slider: QSlider, c_value_lbl=QLabel):
            value = slider.value()

            c_value_lbl.setText("C Value: " + str(value))
            # Save a configuration
            shared_config["c_value"] = value  # Example for another widget
            print(shared_config)

        self.c_val_slider.valueChanged.connect(lambda: _c_value_changed(self.c_val_slider, self.c_val_lbl))

    def _log_transform_clicked(self):
        layer = self.viewer.layers.selection.active
        img_data = layer.data
        img2 = log_transformation(img_data)
        self.viewer.add_image(img2, name="log transform")

    # def _sub_region_changed(self, slider: QSlider, sub_region_label: QLabel):
    #     value = str(slider.value())
    #     sub_region_label.setText("Sub region size: " + value + "×" + value)

    def do_adaptive_thresh(self, viewer):
        layer = self.viewer.layers.selection.active
        img_data = layer.data
        img2 = adaptive_thresh(img_data, self.sub_region.value(), self.c_val_slider.value())
        if "Adaptive Thresh" in self.viewer.layers:
            self.viewer.layers["Adaptive Thresh"].data = img2
            print("right here")
        else:
            self.viewer.add_image(img2, name="Adaptive Thresh")
        self.viewer.layers.selection.active = layer

    def _enable_disable(self):
        if self.enablePrep.isChecked():
            # print("ischecked")
            self.thebtn.setEnabled(True)
            self.tfield.setEnabled(True)
        else:
            # print("not checked")
            self.thebtn.setEnabled(False)
            self.tfield.setEnabled(False)

    def _changed(self, gbox: QGroupBox):
        print(gbox.isChecked())
