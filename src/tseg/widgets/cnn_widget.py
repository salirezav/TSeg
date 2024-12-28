from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel, QCheckBox, QPushButton, QSpinBox, QDoubleSpinBox, QSizePolicy, QSpacerItem, QFrame, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from pathlib import Path
from napari.qt.threading import create_worker
from plantseg.tasks.io_tasks import import_image_task
from plantseg.tasks.prediction_tasks import unet_prediction_task
from plantseg.core.zoo import ModelZoo
from .load_files import load_images_to_viewer
from ..config import shared_config
from plantseg import PATH_MODEL_ZOO, PATH_MODEL_ZOO_CUSTOM
import cellpose.models  # Import CellPose models
from cellpose import io
from enum import Enum


class ImageLayout(Enum):
    YX = "YX"
    CYX = "CYX"
    ZYX = "ZYX"
    CZYX = "CZYX"
    ZCYX = "ZCYX"

    @classmethod
    def to_choices(cls) -> list[str]:
        return [il.value for il in cls]


class CNNWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QVBoxLayout(self)

        def _populate_image_dropdown(dropdown):
            dropdown.clear()
            dropdown.addItem("-select image-")
            image_names = [layer.name for layer in self.viewer.layers if layer._type_string == "image"]
            dropdown.addItems(image_names)

        def _create_plantseg_elements():
            # Initialize Model Zoo and fetch available model names
            ps = PATH_MODEL_ZOO
            psc = PATH_MODEL_ZOO_CUSTOM
            self.model_zoo = ModelZoo(path_zoo=ps, path_zoo_custom=psc)
            self.model_names = self.model_zoo.get_model_names()

            # PlantSeg Section
            plantsegLabel = QLabel("PlantSeg Models")
            plantsegLabel.setAlignment(Qt.AlignLeft)
            plantsegLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
            layout.addWidget(plantsegLabel)

            formLayout = QFormLayout()
            layout.addLayout(formLayout)

            # Image to Use Dropdown
            self.plantsegImageDD = QComboBox(self)
            _populate_image_dropdown(self.plantsegImageDD)
            self.plantsegImageDD.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # CNN Models Dropdown
            self.cnnModelsDD = QComboBox(self)
            self.cnnModelsDD.addItems(self.model_names)
            self.cnnModelsDD.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # Create SpinBoxes for Patch Size and Stride
            def create_spinbox(default_value, minimum=1, maximum=512, tooltip=None):
                spinbox = QSpinBox()
                spinbox.setRange(minimum, maximum)
                spinbox.setValue(default_value)
                spinbox.setMaximumWidth(50)
                if tooltip:
                    spinbox.setToolTip(tooltip)
                return spinbox

            # Patch size inputs
            self.patchsizeZ = create_spinbox(1, tooltip="Patch Size Z")
            self.patchsizeX = create_spinbox(128, tooltip="Patch Size X")
            self.patchsizeY = create_spinbox(128, tooltip="Patch Size Y")
            patchSizeLayout = QHBoxLayout()
            patchSizeLayout.addWidget(self.patchsizeZ)
            patchSizeLayout.addWidget(self.patchsizeX)
            patchSizeLayout.addWidget(self.patchsizeY)

            # Stride inputs
            self.strideZ = create_spinbox(1, tooltip="Stride Z")
            self.strideX = create_spinbox(64, tooltip="Stride X")
            self.strideY = create_spinbox(64, tooltip="Stride Y")
            strideLayout = QHBoxLayout()
            strideLayout.addWidget(self.strideZ)
            strideLayout.addWidget(self.strideX)
            strideLayout.addWidget(self.strideY)

            # Stack Layout Radio Buttons
            self.stackLayoutGroup = QButtonGroup(self)
            stackLayoutHBox = QHBoxLayout()
            for layout_choice in ImageLayout.to_choices():
                radio_button = QRadioButton(layout_choice)
                self.stackLayoutGroup.addButton(radio_button)
                stackLayoutHBox.addWidget(radio_button)
            self.stackLayoutGroup.buttons()[0].setChecked(True)  # Set default selection

            # Checkboxes
            self.useCuda = QCheckBox()
            self.progressLabel = QLabel("")  # Progress label
            self.progressLabel.setMaximumWidth(300)
            self.progressLabel.setMaximumHeight(50)

            # Execute Button
            self.plantsegExecuteBtn = QPushButton("Execute")
            self.plantsegExecuteBtn.clicked.connect(self._start_cnn_detection)

            # Add Widgets to the Layout
            formLayout.addRow("Image to Use", self.plantsegImageDD)
            formLayout.addRow("CNN Model", self.cnnModelsDD)
            formLayout.addRow("Patch Size (Z,X,Y)", patchSizeLayout)
            formLayout.addRow("Stride (Z,X,Y)", strideLayout)
            formLayout.addRow("Stack Layout", stackLayoutHBox)
            formLayout.addRow("Use CUDA?", self.useCuda)
            formLayout.addRow(self.plantsegExecuteBtn)
            formLayout.addRow(self.progressLabel)

        def _create_cellpose_elements():
            # CellPose Section
            cellposeLabel = QLabel("CellPose Models")
            cellposeLabel.setAlignment(Qt.AlignLeft)
            cellposeLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
            layout.addWidget(cellposeLabel)

            formLayout = QFormLayout()
            layout.addLayout(formLayout)

            # Image to Use Dropdown
            self.cellposeImageDD = QComboBox(self)
            _populate_image_dropdown(self.cellposeImageDD)
            self.cellposeImageDD.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # CellPose Models Dropdown
            self.cellposeModelsDD = QComboBox(self)
            self.cellposeModelsDD.addItems(self.cellpose_model_names)
            self.cellposeModelsDD.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # Mean Diameter SpinBox
            self.meanDiameter = QDoubleSpinBox()
            self.meanDiameter.setRange(0.0, 1000.0)
            self.meanDiameter.setValue(30.0)
            self.meanDiameter.setMaximumWidth(50)
            self.meanDiameter.setToolTip("Mean Diameter")

            # Use GPU Checkbox
            self.useGpu = QCheckBox()
            self.cellposeProgressLabel = QLabel("")  # Progress label
            self.cellposeProgressLabel.setMaximumWidth(300)
            self.cellposeProgressLabel.setMaximumHeight(50)

            # Execute Button
            self.cellposeExecuteBtn = QPushButton("Execute")
            self.cellposeExecuteBtn.clicked.connect(self._start_cellpose_detection)

            # Add Widgets to the Layout
            formLayout.addRow("Image to Use", self.cellposeImageDD)
            formLayout.addRow("CellPose Model", self.cellposeModelsDD)
            formLayout.addRow("Mean Diameter", self.meanDiameter)
            formLayout.addRow("Use GPU?", self.useGpu)
            formLayout.addRow(self.cellposeExecuteBtn)
            formLayout.addRow(self.cellposeProgressLabel)

        self.cellpose_model_names = cellpose.models.MODEL_NAMES  # Define cellpose_model_names

        _create_plantseg_elements()
        layout.addWidget(QFrame(frameShape=QFrame.HLine))  # Add horizontal divider
        _create_cellpose_elements()

        # Connect layer events to update dropdowns
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.plantsegImageDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.plantsegImageDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.plantsegImageDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.cellposeImageDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.cellposeImageDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.cellposeImageDD))

    def _start_cnn_detection(self):
        patch_size = (self.patchsizeZ.value(), self.patchsizeX.value(), self.patchsizeY.value())
        stride_size = (self.strideZ.value(), self.strideX.value(), self.strideY.value())
        use_cuda = self.useCuda.isChecked()
        selected_image = self.plantsegImageDD.currentText()
        files_to_use = shared_config.get("selected_files", [])

        if selected_image == "-select image-":
            self.progressLabel.setText("No image selected!")
            return

        # Extract the path of the selected image
        selected_layer = self.viewer.layers[selected_image]
        selected_image_path = selected_layer.metadata.get("path", "")

        # Get selected stack layout
        stack_layout = self.stackLayoutGroup.checkedButton().text()

        input_path = Path(selected_image_path)
        selected_model = self.cnnModelsDD.currentText()
        self.progressLabel.setText(f"Starting CNN prediction with model: {selected_model}...")
        self.plantsegExecuteBtn.setEnabled(False)

        # Worker task function
        def worker_task():
            plantseg_image = import_image_task(input_path=input_path, semantic_type="raw", stack_layout=stack_layout)
            return unet_prediction_task(
                image=plantseg_image,
                model_name=selected_model,
                model_id=None,
                suffix="_prediction",
                patch=patch_size,
                device="cuda" if use_cuda else "cpu",
                # patch_halo=stride_size,
            )

        # Callback when the worker is done
        def on_done(predicted_images):
            self.progressLabel.setText("Prediction complete!")
            self.viewer.add_image(predicted_images[0].get_data(), name=f"{selected_image} {selected_model} mask")
            self.plantsegExecuteBtn.setEnabled(True)
            # load_images_to_viewer(self.viewer, predicted_images)

        # Handle errors
        def on_error(exception):
            self.progressLabel.setText(f"Error: {exception}")
            self.plantsegExecuteBtn.setEnabled(True)

        # Create and start the worker
        worker = create_worker(worker_task)
        worker.returned.connect(on_done)
        worker.errored.connect(on_error)
        worker.start()
        self.progressLabel.setText("Prediction started...")

    def _start_cellpose_detection(self):
        selected_model = self.cellposeModelsDD.currentText()
        use_gpu = self.useGpu.isChecked()
        mean_diameter = self.meanDiameter.value()
        selected_image = self.cellposeImageDD.currentText()
        files_to_use = shared_config.get("selected_files", [])

        if selected_image == "-select image-":
            self.cellposeProgressLabel.setText("No image selected!")
            return

        # Extract the path of the selected image
        selected_layer = self.viewer.layers[selected_image]
        selected_image_path = selected_layer.metadata.get("path", "")

        input_path = Path(selected_image_path)
        self.cellposeProgressLabel.setText(f"Starting CellPose prediction with model: {selected_model}...")
        self.cellposeExecuteBtn.setEnabled(False)

        # Worker task function
        def worker_task():
            image = io.imread(input_path)
            model = cellpose.models.Cellpose(gpu=use_gpu, model_type=selected_model)
            masks, flows, styles, diams = model.eval(image, diameter=mean_diameter, channels=[0, 0], flow_threshold=0.4, cellprob_threshold=0)
            return masks

        # Callback when the worker is done
        def on_done(masks):
            self.cellposeProgressLabel.setText("Prediction complete!")
            self.viewer.add_image(masks, name=f"{selected_image} {selected_model} mask")
            self.cellposeExecuteBtn.setEnabled(True)
            # load_images_to_viewer(self.viewer, masks)

        # Handle errors
        def on_error(exception):
            self.cellposeProgressLabel.setText(f"Error: {exception}")
            self.cellposeExecuteBtn.setEnabled(True)

        # Create and start the worker
        worker = create_worker(worker_task)
        worker.returned.connect(on_done)
        worker.errored.connect(on_error)
        worker.start()
        self.cellposeProgressLabel.setText("Prediction started...")
