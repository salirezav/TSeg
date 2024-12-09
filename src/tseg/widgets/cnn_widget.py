from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from .load_files import *

from ..config import *


CNNMODELS = [
    "generic confocal_3d_unet",
    "generic_light_sheet_3d_unet",
    "confocal_unet_bce_dice_ds 1x",
    "confocal_unet_bce_dice_ds2x",
    "confocal_unet_bce_dice_ds3x",
    "confocal_2D_unet_bce_dice_ds 1x",
    "confocal_2D_unet_bce_dice_ds2x",
    "confocal_2D_unet_bce_dice_ds3x",
    "confocal_unet_bce_dice_nuclei_stain_ds 1x",
    "lightsheet_unet_bce_dice_ds1x",
    "lightsheet_unet_bce_dice_nuclei_dsix",
    "lightsheet_unet_bce_dice_ds2x",
    "lightsheet_unet_bce_dice_ds3x",
    "confocal_PNAS_20",
    "confocal_PNAS_30",
]


class CNNWidget(QWidget):

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QGridLayout(self)
        gbox = QGroupBox("CNN Prediction", checkable=True)
        layout.addWidget(gbox)

        gridLayout = QGridLayout()
        gbox.setLayout(gridLayout)
        cnnModelsDD = QComboBox(self)
        cnnModelsDD.addItems([item for item in CNNMODELS])
        patchsizeZ, patchsizeX, patchsizeY = QLineEdit(), QLineEdit(), QLineEdit()
        strideZ, strideX, strideY = QLineEdit(), QLineEdit(), QLineEdit()
        patchsizeZ.setToolTip("Z")
        patchsizeX.setToolTip("X")
        patchsizeY.setToolTip("Y")
        strideZ.setToolTip("Z")
        strideX.setToolTip("X")
        strideY.setToolTip("Y")
        patchsizeZ.setAlignment(Qt.AlignCenter)
        patchsizeX.setAlignment(Qt.AlignCenter)
        patchsizeY.setAlignment(Qt.AlignCenter)
        strideZ.setAlignment(Qt.AlignCenter)
        strideX.setAlignment(Qt.AlignCenter)
        strideY.setAlignment(Qt.AlignCenter)
        useCuda = QCheckBox()
        outTiff = QCheckBox()

        btn = QPushButton("Execute")
        btn.clicked.connect(lambda: self._execute_cnn_detection())

        gridLayout.addWidget(QLabel("CNN Model"), 0, 0)
        gridLayout.addWidget(cnnModelsDD, 0, 1, 1, 3)
        gridLayout.addWidget(QLabel("Patch Size (Z,X,Y)"), 1, 0)
        gridLayout.addWidget(patchsizeZ, 1, 1)
        gridLayout.addWidget(patchsizeX, 1, 2)
        gridLayout.addWidget(patchsizeY, 1, 3)
        gridLayout.addWidget(QLabel("Stride (Z,X,Y)"), 2, 0)
        gridLayout.addWidget(strideZ, 2, 1)
        gridLayout.addWidget(strideX, 2, 2)
        gridLayout.addWidget(strideY, 2, 3)
        gridLayout.addWidget(QLabel("Use CUDA?"), 3, 0)
        gridLayout.addWidget(useCuda, 3, 1)
        gridLayout.addWidget(QLabel("Output .tif?"), 4, 0)
        gridLayout.addWidget(outTiff, 4, 1)
        gridLayout.addWidget(btn, 5, 0, 6, 5)

    def _execute_cnn_detection(self):

        # # IOWidget = self.viewer.window._qt_window.findChild(QWidget, name="tseg: Input/Output").findChild(QGridLayout).findChild(QGroupBox).findChild(QLineEdit, name="outputDirName")
        # # dirname = IOWidget.findChild(QLineEdit, name="outputDirName")
        # dirname = shared_config.get("output_dir")
        # print(dirname)
        # output_dir = dirname
        for layer in self.viewer.layers:
            save_to_output_dir(layer.data, layer.name, output_dir)
