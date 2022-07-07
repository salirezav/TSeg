"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
import tifffile
from .load_files import *
from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from qtpy.QtWidgets import *
from PyQt5.QtCore import *
from enum import Enum
import os

if TYPE_CHECKING:
    import napari


CNNMODELS = ["generic confocal_3d_unet",
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
             "confocal_PNAS_30"]
STRIDES = ["Accurate", "Balanced", "Draft"]
SEGMENTATION_ALGORITHMS = ["MutexWS", "GASP",
                           "Simple TK", "MultiCut", "DtWatershed", ]
Input_Files = []


class InputOutputWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.Selected_Files = list()
        self.file_radiobutton = QRadioButton("Select Files")
        self.file_radiobutton.setChecked(True)
        self.file_radiobutton.clicked.connect(self._file_radio_clicked)
        self.directory_radiobutton = QRadioButton("Select Directory")
        self.directory_radiobutton.clicked.connect(self._dir_radio_clicked)
        radioHBox = QHBoxLayout()
        radioHBox.addWidget(self.file_radiobutton)
        radioHBox.addWidget(self.directory_radiobutton)

        layout = QGridLayout(self)
        inputGroupBox = QGroupBox(
            "Input: Select files or a directory", checkable=False)
        outputGroupBox = QGroupBox("Output. Specify the output folder name")
        layout.addWidget(inputGroupBox)
        totalVBox = QVBoxLayout()
        outputForm = QFormLayout()
        self.outputDirName = QLineEdit(os.path.join(
            os.path.expanduser('~'), "tseg_output"))
        outputForm.addRow("Output directory name", self.outputDirName)
        inputGroupBox.setLayout(totalVBox)
        outputGroupBox.setLayout(outputForm)
        # layout.addLayout(outputForm,0,1)
        totalVBox.addLayout(radioHBox)
        # totalVBox.addStretch()
        layout.addWidget(outputGroupBox)

        self.zsliceLbl = QLabel("Number of Z-slices:")
        self.numZslices = QLineEdit()
        self.loadButton = QPushButton("Load Files to the viewer")
        self.nextBtn = QPushButton("Next")
        self.nextBtn.setStyleSheet("""
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
                                   """)

        self.fileStack = QWidget()
        self.dirStack = QWidget()

        self.fileStackUI()
        self.dirStackUI()

        self.loadButton.clicked.connect(
            lambda: self._load_files_to_viewer(self.viewer))

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.fileStack)
        self.Stack.addWidget(self.dirStack)

        zsliceHbox = QHBoxLayout()
        zsliceHbox.addWidget(self.zsliceLbl)
        zsliceHbox.addWidget(self.numZslices)

        totalVBox.addWidget(self.Stack)

        totalVBox.addLayout(zsliceHbox)
        totalVBox.addWidget(self.loadButton)
        layout.addWidget(self.nextBtn)

    def _load_files_to_viewer(self, napari_viewer):
        print(self.Selected_Files)
        loaded = load_as_nparray(self.Selected_Files)
        # print(loaded)
        for image in loaded:
            napari_viewer.add_image(image["image_data"], name=image["name"])

    def _file_radio_clicked(self):
        self.displayStack(0)

    def _dir_radio_clicked(self):
        self.displayStack(1)

    def fileStackUI(self):
        layout = QHBoxLayout()
        self.listOfFiles = QListWidget()
        self.browseFiles = QPushButton("Select Files")
        self.browseFiles.clicked.connect(
            lambda: self._file_on_click(self.listOfFiles))
        layout.addWidget(self.listOfFiles)
        layout.addWidget(self.browseFiles)

        self.fileStack.setLayout(layout)

    def dirStackUI(self):
        layout = QHBoxLayout()

        self.dirLineEdit = QLineEdit("path/to/directory")
        self.browseDir = QPushButton("Select Directory")
        self.browseDir.clicked.connect(
            lambda: self._dir_on_click(self.dirLineEdit))

        layout.addWidget(self.dirLineEdit)
        layout.addWidget(self.browseDir)
        self.dirStack.setLayout(layout)

    def displayStack(self, i):
        self.Stack.setCurrentIndex(i)

    def _file_on_click(self, fileListWidget: QListWidget):
        self.Selected_Files, _ = QFileDialog.getOpenFileNames(
            self, "select one or more files to open", os.path.expanduser('~'), "Images (*.tif *.tiff)")
        # print(files)
        # self.Selected_Files = files
        # for item in self.Selected_Files:
        #     print(os.path.basename(item))
        for i, fileName in enumerate(self.Selected_Files):
            fileListWidget.insertItem(i, fileName)
            # fileListWidget.insertItem(i, fileName.split('/')[-1])

    def _dir_on_click(self, dirLineEdit: QLineEdit):
        directory = QFileDialog.getExistingDirectory(
            self, caption="Select the desired directory.")
        dirLineEdit.setText(directory)
        # print(directory)


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

        tfield = QLineEdit("stuff will be here")
        vbox.addWidget(tfield)
        # self.tfield.setEnabled(False)

    def _enable_disable(self):
        if self.enablePrep.isChecked():
            print("ischecked")
            self.thebtn.setEnabled(True)
            self.tfield.setEnabled(True)
        else:
            print("not checked")
            self.thebtn.setEnabled(False)
            self.tfield.setEnabled(False)

    def _changed(self, gbox: QGroupBox):
        print(gbox.isChecked())


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
        gridLayout.addWidget(
            QLabel("Under/Over segmentation factor:"), 2, 0, 2, 1)
        self.UnderOverFactorSldr = QSlider(Qt.Horizontal)
        self.UnderOverFactorSldr.setMinimum(1)
        self.UnderOverFactorSldr.setMaximum(99)
        self.UnderOverFactorSldr.setValue(60)
        self.UnderOverFactorSldr.setPageStep(10)
        self.UnderOverFactorSldr.setTickInterval(1)
        self.UnderOverFactorSldr.setSingleStep(0.01)

        self.UnderOverFactorSldr.setTickPosition(
            QSlider.TickPosition.TicksBelow)
        self.factorValue = QLineEdit("0.6")
        self.UnderOverFactorSldr.valueChanged.connect(
            lambda: self._factorChanged(self.UnderOverFactorSldr.value(), self.factorValue))
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
        gridLayout.addWidget(
            QLabel("Superpixels Minimum Size (Voxels)"), 12, 0, 2, 1)
        self.superpixMinSize = QLineEdit()
        gridLayout.addWidget(self.superpixMinSize, 12, 1, 2, 2)
        ###
        # cellMinSize
        ###
        gridLayout.addWidget(QLabel("Cell Minimum Size (Voxels)"), 14, 0, 2, 1)
        self.cellMinSize = QLineEdit()
        gridLayout.addWidget(self.cellMinSize, 14, 1, 2, 2)

    def _factorChanged(self, value: int, factorValue: QLineEdit):
        factorValue.setText(str(value/100))


class TrackingWidget(QWidget):
    def __init__(self, napari_viewer):
        pass


class ClassificationWidget(QWidget):
    def __init__(self, napari_viewer):
        pass
