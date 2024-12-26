from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QComboBox, QLabel, QCheckBox, QPushButton, QSpinBox, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt
from pathlib import Path
from napari.qt.threading import create_worker
from plantseg.tasks.io_tasks import import_image_task
from plantseg.tasks.prediction_tasks import unet_prediction_task
from plantseg.core.zoo import ModelZoo
from .load_files import load_images_to_viewer
from ..config import shared_config
import plantseg


class CNNWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QGridLayout(self)

        # Initialize Model Zoo and fetch available model names
        ps = plantseg.PATH_MODEL_ZOO
        psc = plantseg.PATH_MODEL_ZOO_CUSTOM
        self.model_zoo = ModelZoo(path_zoo=ps, path_zoo_custom=psc)
        self.model_names = self.model_zoo.get_model_names()

        # Main GroupBox
        gbox = QGroupBox("PlantSeg Models", checkable=True)
        gbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(gbox, 0, 0, Qt.AlignTop | Qt.AlignHCenter)

        gridLayout = QGridLayout()
        gbox.setLayout(gridLayout)

        # CNN Models Dropdown
        self.cnnModelsDD = QComboBox(self)
        self.cnnModelsDD.addItems(self.model_names)
        self.cnnModelsDD.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Create SpinBoxes for Patch Size and Stride
        def create_spinbox(default_value, minimum=1, maximum=512, tooltip=None):
            spinbox = QSpinBox()
            spinbox.setRange(minimum, maximum)
            spinbox.setValue(default_value)
            spinbox.setMaximumWidth(10)
            if tooltip:
                spinbox.setToolTip(tooltip)
            return spinbox

        # Patch size inputs
        self.patchsizeZ = create_spinbox(1, tooltip="Patch Size Z")
        self.patchsizeX = create_spinbox(128, tooltip="Patch Size X")
        self.patchsizeY = create_spinbox(128, tooltip="Patch Size Y")

        # Stride inputs
        self.strideZ = create_spinbox(1, tooltip="Stride Z")
        self.strideX = create_spinbox(64, tooltip="Stride X")
        self.strideY = create_spinbox(64, tooltip="Stride Y")

        # Checkboxes
        self.useCuda = QCheckBox()
        self.progressLabel = QLabel("")  # Progress label

        # Execute Button
        btn = QPushButton("Execute")
        btn.clicked.connect(self._start_cnn_detection)

        # Add Widgets to the Layout
        gridLayout.addWidget(QLabel("CNN Model"), 0, 0)
        gridLayout.addWidget(self.cnnModelsDD, 0, 1, 1, 3)

        gridLayout.addWidget(QLabel("Patch Size (Z,X,Y)"), 1, 0)
        gridLayout.addWidget(self.patchsizeZ, 1, 1)
        gridLayout.addWidget(self.patchsizeX, 1, 2)
        gridLayout.addWidget(self.patchsizeY, 1, 3)

        gridLayout.addWidget(QLabel("Stride (Z,X,Y)"), 2, 0)
        gridLayout.addWidget(self.strideZ, 2, 1)
        gridLayout.addWidget(self.strideX, 2, 2)
        gridLayout.addWidget(self.strideY, 2, 3)

        gridLayout.addWidget(QLabel("Use CUDA?"), 3, 0)
        gridLayout.addWidget(self.useCuda, 3, 1)

        gridLayout.addWidget(btn, 4, 0, 1, 4, alignment=Qt.AlignCenter)
        gridLayout.addWidget(self.progressLabel, 5, 0, 1, 4)

        gridLayout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), 6, 0)

    def _start_cnn_detection(self):
        patch_size = (self.patchsizeZ.value(), self.patchsizeX.value(), self.patchsizeY.value())
        stride_size = (self.strideZ.value(), self.strideX.value(), self.strideY.value())
        use_cuda = self.useCuda.isChecked()
        files_to_use = shared_config.get("selected_files", [])

        if not files_to_use:
            self.progressLabel.setText("No files selected!")
            return

        input_path = Path(files_to_use[0])
        selected_model = self.cnnModelsDD.currentText()
        self.progressLabel.setText(f"Starting CNN prediction with model: {selected_model}...")

        # Worker task function
        def worker_task():
            plantseg_image = import_image_task(input_path=input_path, semantic_type="raw", stack_layout="YX")
            return unet_prediction_task(
                image=plantseg_image,
                model_name=selected_model,
                model_id=None,
                suffix="_prediction",
                patch=patch_size,
                # stride=stride_size,
                # device="cuda" if use_cuda else "cpu",
            )

        # Callback when the worker is done
        def on_done(predicted_images):
            self.progressLabel.setText("Prediction complete!")
            self.viewer.add_image(predicted_images[0].get_data())
            # load_images_to_viewer(self.viewer, predicted_images)

        # Handle errors
        def on_error(exception):
            self.progressLabel.setText(f"Error: {exception}")

        # Create and start the worker
        worker = create_worker(worker_task)
        worker.returned.connect(on_done)
        worker.errored.connect(on_error)
        worker.start()
        self.progressLabel.setText("Prediction started...")
