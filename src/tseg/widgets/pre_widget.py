import os
from pathlib import Path
from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
import tifffile
from tseg.config import shared_config  # Import shared_config

from tseg.widgets.prep import *


class PreProcessingWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QVBoxLayout(self)

        hintLabel = QLabel("Hint: Select the layer(s) you want to process in the layer list and then click the button.")

        layout.addWidget(hintLabel)

        # Convert to Grayscale Section
        grayscaleLabel = QLabel("Convert to Grayscale")
        grayscaleLabel.setAlignment(Qt.AlignLeft)
        grayscaleLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(grayscaleLabel)

        grayscaleFormLayout = QFormLayout()
        layout.addLayout(grayscaleFormLayout)

        self.grayscaleButton = QPushButton("To Grayscale")
        self.grayscaleButton.setStyleSheet(
            """
            QPushButton{
            background-color: #198754;
            border-color: #28a745;
            }
            QPushButton::hover
            {
            background-color: #218838;
            border-color: #1e7e34;
            }
            QPushButton::pressed
            {
            background-color: #1e7e34;
            border-color: #1c7430;
            }
            """
        )
        self.grayscaleButton.clicked.connect(lambda: self.convert_to_grayscale(self.viewer))

        grayscaleFormLayout.addRow(grayscaleLabel, self.grayscaleButton)

        layout.addWidget(QFrame(frameShape=QFrame.HLine))  # Add horizontal divider

        # Normalization Section
        normalizationLabel = QLabel("Normalization")
        normalizationLabel.setAlignment(Qt.AlignLeft)
        normalizationLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(normalizationLabel)

        normFormLayout = QFormLayout()
        layout.addLayout(normFormLayout)

        self.normGroup = QButtonGroup(self)
        self.minMaxNorm = QRadioButton("Min-Max")
        self.scaleNorm = QRadioButton("Scale to -1,+1")
        self.zScoreNorm = QRadioButton("Z-Score")
        self.histEqNorm = QRadioButton("Hist Eq")
        self.gammaCorrNorm = QRadioButton("Gamma Correction")
        self.normGroup.addButton(self.minMaxNorm)
        self.normGroup.addButton(self.scaleNorm)
        self.normGroup.addButton(self.zScoreNorm)
        self.normGroup.addButton(self.histEqNorm)
        self.normGroup.addButton(self.gammaCorrNorm)
        self.minMaxNorm.setChecked(True)  # Set default selection

        self.gammaSpinBox = QDoubleSpinBox()
        self.gammaSpinBox.setRange(0.0, 2.0)
        self.gammaSpinBox.setSingleStep(0.1)
        self.gammaSpinBox.setValue(1.0)
        self.gammaSpinBox.setMaximumWidth(50)

        normLayout = QVBoxLayout()
        normLayout.addWidget(self.minMaxNorm)
        normLayout.addWidget(self.scaleNorm)
        normLayout.addWidget(self.zScoreNorm)
        normLayout.addWidget(self.histEqNorm)

        gammaLayout = QHBoxLayout()
        gammaLayout.addWidget(self.gammaCorrNorm)
        gammaLayout.addWidget(self.gammaSpinBox)
        normLayout.addLayout(gammaLayout)

        self.normButton = QPushButton("Normalize")
        self.normButton.setStyleSheet(
            """
            QPushButton{
            background-color: #198754;
            border-color: #28a745;
            }
            QPushButton::hover
            {
            background-color: #218838;
            border-color: #1e7e34;
            }
            QPushButton::pressed
            {
            background-color: #1e7e34;
            border-color: #1c7430;
            }
            """
        )
        self.normButton.clicked.connect(lambda: self.do_normalization(self.viewer))

        normFormLayout.addRow("Normalization", normLayout)
        normFormLayout.addRow(self.normButton)

        layout.addWidget(QFrame(frameShape=QFrame.HLine))  # Add horizontal divider

        # Adaptive Threshold Section
        adaptiveThreshLabel = QLabel("Adaptive Threshold")
        adaptiveThreshLabel.setAlignment(Qt.AlignLeft)
        adaptiveThreshLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(adaptiveThreshLabel)

        threshFormLayout = QFormLayout()
        layout.addLayout(threshFormLayout)

        self.adap = QPushButton("Adaptive Thresholding")
        self.adap.setStyleSheet(
            """
            QPushButton{
            background-color: #198754;
            border-color: #28a745;
            }
            QPushButton::hover
            {
            background-color: #218838;
            border-color: #1e7e34;
            }
            QPushButton::pressed
            {
            background-color: #1e7e34;
            border-color: #1c7430;
            }
            """
        )
        self.sub_region = QSlider(Qt.Horizontal)
        self.sub_region.setMinimum(3)
        self.sub_region.setMaximum(100)
        self.sub_region.setValue(9)
        self.sub_region.setTickInterval(2)
        self.sub_region.setSingleStep(2)
        self.sub_region.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sub_region_lbl = QLabel("Sub region size: " + str(self.sub_region.value()) + "×" + str(self.sub_region.value()))

        self.c_val_slider = QSlider(Qt.Horizontal)
        self.c_val_slider.setMinimum(1)
        self.c_val_slider.setMaximum(100)
        self.c_val_slider.setValue(5)
        self.c_val_lbl = QLabel("C Value: " + str(self.c_val_slider.value()))

        self.logTrans = QPushButton("Log transform")
        self.logTrans.clicked.connect(lambda: self._log_transform_clicked())

        threshFormLayout.addRow(self.sub_region_lbl, self.sub_region)
        threshFormLayout.addRow(self.c_val_lbl, self.c_val_slider)
        threshFormLayout.addRow(self.adap)

        self.adap.clicked.connect(lambda: self.do_adaptive_thresh(self.viewer))

        layout.addWidget(QFrame(frameShape=QFrame.HLine))  # Add horizontal divider

        # Contrast Limit Section
        contrastLimitLabel = QLabel("Contrast Limit")
        contrastLimitLabel.setAlignment(Qt.AlignLeft)
        contrastLimitLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(contrastLimitLabel)

        contrastFormLayout = QFormLayout()
        layout.addLayout(contrastFormLayout)

        self.contrastButton = QPushButton("Apply Contrast Limit")
        self.contrastButton.setStyleSheet(
            """
            QPushButton{
            background-color: #198754;
            border-color: #28a745;
            }
            QPushButton::hover
            {
            background-color: #218838;
            border-color: #1e7e34;
            }
            QPushButton::pressed
            {
            background-color: #1e7e34;
            border-color: #1c7430;
            }
            """
        )
        self.contrastButton.clicked.connect(lambda: self.apply_contrast_limit(self.viewer))

        contrastFormLayout.addRow(self.contrastButton)

        self.output_dir = Path.home() / ".tseg"
        self.output_dir.mkdir(exist_ok=True)

        def _sub_region_changed(slider, label):
            value = slider.value()
            if value % 2 == 0:
                value += 1 if value < slider.maximum() else -1
                slider.setValue(value)
            label.setText(f"Sub region size: {value}×{value}")
            shared_config["sub_region"] = self.sub_region.value()
            print(shared_config)

        self.sub_region.valueChanged.connect(lambda: _sub_region_changed(self.sub_region, self.sub_region_lbl))

        def _c_value_changed(slider: QSlider, c_value_lbl=QLabel):
            value = slider.value()
            c_value_lbl.setText("C Value: " + str(value))
            shared_config["c_value"] = value
            print(shared_config)

        self.c_val_slider.valueChanged.connect(lambda: _c_value_changed(self.c_val_slider, self.c_val_lbl))

    def _log_transform_clicked(self):
        layer = self.viewer.layers.selection.active
        img_data = layer.data
        img2 = log_transformation(img_data)
        self.viewer.add_image(img2, name="log transform")

    def _save_image(self, image, original_name, suffix):
        # Ensure the image is properly formatted for saving
        if len(image.shape) == 3 and image.shape[0] not in [1, 3, 4]:
            image = np.moveaxis(image, 0, -1)  # Move channels to the last dimension
        output_path = self.output_dir / f"{original_name}_{suffix}.tif"
        if len(image.shape) >= 3:
            tifffile.imwrite(str(output_path), image)
        else:
            cv2.imwrite(str(output_path), image)
        return output_path

    def convert_to_grayscale(self, viewer):
        selected_layers = [layer for layer in self.viewer.layers.selection]
        for layer in selected_layers:
            img_data = layer.data
            img2 = preprocess_image(img_data, convert_to_grayscale)
            new_layer_name = f"{layer.name}_grayscale"
            output_path = self._save_image(img2, layer.name, "grayscale")
            new_layer = self.viewer.add_image(img2, name=new_layer_name)
            new_layer.metadata["path"] = str(output_path)
        self.viewer.layers.selection.active = selected_layers[0] if selected_layers else None

    def do_adaptive_thresh(self, viewer):
        selected_layers = [layer for layer in self.viewer.layers.selection]
        for layer in selected_layers:
            img_data = layer.data
            img2 = preprocess_image(img_data, adaptive_thresh, sub_region=self.sub_region.value(), c_value=self.c_val_slider.value())
            new_layer_name = f"{layer.name}_AdaptiveThresh"
            output_path = self._save_image(img2, layer.name, "AdaptiveThresh")
            new_layer = self.viewer.add_image(img2, name=new_layer_name)
            new_layer.metadata["path"] = str(output_path)
        self.viewer.layers.selection.active = selected_layers[0] if selected_layers else None

    def do_normalization(self, viewer):
        selected_layers = [layer for layer in self.viewer.layers.selection]
        norm_type = self.normGroup.checkedButton().text()
        for layer in selected_layers:
            img_data = layer.data
            if norm_type == "Min-Max":
                img2 = preprocess_image(img_data, min_max_normalization)
            elif norm_type == "Scale to -1,+1":
                img2 = preprocess_image(img_data, scale_to_minus1_plus1)
            elif norm_type == "Z-Score":
                img2 = preprocess_image(img_data, z_score_normalization)
            elif norm_type == "Hist Eq":
                img2 = preprocess_image(img_data, histogram_equalization)
            elif norm_type == "Gamma Correction":
                img2 = preprocess_image(img_data, gamma_correction, gamma=self.gammaSpinBox.value())
            new_layer_name = f"{layer.name}_normalized"
            output_path = self._save_image(img2, layer.name, "normalized")
            new_layer = self.viewer.add_image(img2, name=new_layer_name)
            new_layer.metadata["path"] = str(output_path)
        self.viewer.layers.selection.active = selected_layers[0] if selected_layers else None

    def apply_contrast_limit(self, viewer):
        selected_layers = [layer for layer in self.viewer.layers.selection]
        for layer in selected_layers:
            img_data = layer.data
            # Retrieve contrast limits from the layer controls panel
            min_val, max_val = layer.contrast_limits
            img2 = preprocess_image(img_data, apply_contrast_limit, min_val=min_val, max_val=max_val)
            new_layer_name = f"{layer.name}_contrast"
            output_path = self._save_image(img2, layer.name, "contrast")
            new_layer = self.viewer.add_image(img2, name=new_layer_name)
            new_layer.metadata["path"] = str(output_path)
        self.viewer.layers.selection.active = selected_layers[0] if selected_layers else None

    def _enable_disable(self):
        if self.enablePrep.isChecked():
            self.thebtn.setEnabled(True)
            self.tfield.setEnabled(True)
        else:
            self.thebtn.setEnabled(False)
            self.tfield.setEnabled(False)

    def _changed(self, gbox: QGroupBox):
        print(gbox.isChecked())
