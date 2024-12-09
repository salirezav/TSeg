from qtpy.QtWidgets import *
from qtpy.QtCore import Qt

SEGMENTATION_ALGORITHMS = [
    "MutexWS",
    "GASP",
    "Simple TK",
    "MultiCut",
    "DtWatershed",
]
STRIDES = ["Accurate", "Balanced", "Draft"]

from ..config import shared_config  # Import shared_config

class SegWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        layout = QGridLayout(self)

        gbox = QGroupBox("Segmentation", checkable=True)
        gridLayout = QGridLayout()
        gbox.setLayout(gridLayout)
        layout.addWidget(gbox)

        SegAlgorithmsDD = QComboBox(self)
        SegAlgorithmsDD.addItems([item for item in SEGMENTATION_ALGORITHMS])

        gridLayout.addWidget(QLabel("Algorithm:"), 0, 0, 2, 1)
        gridLayout.addWidget(SegAlgorithmsDD, 0, 1, 2, 4)
        gridLayout.addWidget(QLabel("Under/Over segmentation factor:"), 2, 0, 2, 1)
        self.UnderOverFactorSldr = QSlider(Qt.Horizontal)
        self.UnderOverFactorSldr.setMinimum(1)
        self.UnderOverFactorSldr.setMaximum(99)
        self.UnderOverFactorSldr.setValue(60)
        self.UnderOverFactorSldr.setPageStep(10)
        self.UnderOverFactorSldr.setTickInterval(1)
        self.UnderOverFactorSldr.setSingleStep(1)
        self.UnderOverFactorSldr.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.factorValue = QLineEdit("0.6")
        self.UnderOverFactorSldr.valueChanged.connect(lambda: self._factorChanged(self.UnderOverFactorSldr.value(), self.factorValue))
        gridLayout.addWidget(self.UnderOverFactorSldr, 2, 1, 2, 3)
        gridLayout.addWidget(self.factorValue, 2, 4, 2, 1)

        gridLayout.addWidget(QLabel("Run Watershed in 2D?"), 4, 0, 2, 1)
        self.waterShedIn2d = QCheckBox()
        gridLayout.addWidget(self.waterShedIn2d)

        ###
        # cnnPredThreshSldr
        ###
        gridLayout.addWidget(QLabel("CNN Predictions Threshold"), 6, 0, 2, 1)
        self.cnnPredThreshSldr = QSlider(Qt.Horizontal)
        self.cnnPredThreshVal = QLineEdit("0.500")
        gridLayout.addWidget(self.cnnPredThreshSldr, 6, 1, 2, 3)
        gridLayout.addWidget(self.cnnPredThreshVal, 6, 4, 2, 1)
        ###
        # wtrshedSeedSigSldr
        ###
        gridLayout.addWidget(QLabel("Watershed Seeds Sigma"), 8, 0, 2, 1)
        self.wtrshedSeedSigSldr = QSlider(Qt.Horizontal)
        self.wtrshedSeedSigVal = QLineEdit("2.0")
        gridLayout.addWidget(self.wtrshedSeedSigSldr, 8, 1, 2, 3)
        gridLayout.addWidget(self.wtrshedSeedSigVal, 8, 4, 2, 1)
        ###
        # wtrshedBoundSigSldr
        ###
        gridLayout.addWidget(QLabel("Watershed Boundary Sigma"), 10, 0, 2, 1)
        self.wtrshedBoundSigSldr = QSlider(Qt.Horizontal)
        self.wtrshedBoundSigVal = QLineEdit("0.0")
        gridLayout.addWidget(self.wtrshedBoundSigSldr, 10, 1, 2, 3)
        gridLayout.addWidget(self.wtrshedBoundSigVal, 10, 4, 2, 1)
        ###
        # superpixMinSize
        ###
        gridLayout.addWidget(QLabel("Superpixels Minimum Size (Voxels)"), 12, 0, 2, 1)
        self.superpixMinSize = QLineEdit()
        gridLayout.addWidget(self.superpixMinSize, 12, 1, 2, 2)
        ###
        # cellMinSize
        ###
        gridLayout.addWidget(QLabel("Cell Minimum Size (Voxels)"), 14, 0, 2, 1)
        self.cellMinSize = QLineEdit()
        gridLayout.addWidget(self.cellMinSize, 14, 1, 2, 2)

    def _factorChanged(self, value: int, factorValue: QLineEdit):
        factorValue.setText(str(value / 100))
