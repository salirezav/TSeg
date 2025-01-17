import tifffile
from tseg.widgets.load_files import *
from tseg.widgets.prep import *
from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from enum import Enum
import os

from tseg.config import shared_config  # Import shared_config


class InputOutputWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.Selected_Files = list()
        self.Input_Directory = ""
        self.file_radiobutton = QRadioButton("Select Files")
        self.file_radiobutton.setChecked(True)
        self.file_radiobutton.clicked.connect(self._file_radio_clicked)
        self.directory_radiobutton = QRadioButton("Select Directory")
        self.directory_radiobutton.clicked.connect(self._dir_radio_clicked)
        radioHBox = QHBoxLayout()
        radioHBox.addWidget(self.file_radiobutton)
        radioHBox.addWidget(self.directory_radiobutton)

        layout = QGridLayout(self)
        inputGroupBox = QGroupBox("Input: Select files or a directory", checkable=False)
        outputGroupBox = QGroupBox("Output: Specify the temporary output folder name")
        layout.addWidget(inputGroupBox, 0, 0, Qt.AlignTop)
        totalVBox = QVBoxLayout()
        outputForm = QFormLayout()
        self.outputDirName = QLineEdit(os.path.join(os.path.expanduser("~"), ".tseg"))
        self.outputDirName.textChanged.connect(lambda: self._output_dir_changed(self.outputDirName.text()))
        outputForm.addRow("Output directory path", self.outputDirName)
        inputGroupBox.setLayout(totalVBox)
        outputGroupBox.setLayout(outputForm)
        # layout.addLayout(outputForm,0,1)
        totalVBox.addLayout(radioHBox)
        # totalVBox.addStretch()
        layout.addWidget(outputGroupBox, 1, 0, Qt.AlignTop)

        inputGroupBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        outputGroupBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding), 2, 0)
        # layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 1)

        # self.zsliceLbl = QLabel("Number of Z-slices:")
        # self.numZslices = QLineEdit()
        self.loadButton = QPushButton("Load Files to the viewer")
        self.loadButton.setStyleSheet(TsegStyles.BTN_PRIMARY)
        self.save_as_gray_btn = QPushButton("Save all as grayscale...")
        self.save_as_gray_btn.clicked.connect(lambda: self.save_as_grayscale(napari_viewer))

        self.nextBtn = QPushButton("Next")
        self.nextBtn.setStyleSheet(TsegStyles.BTN_PRIMARY)

        self.nextBtn.clicked.connect(self._io_next)
        self.fileStack = QWidget()
        self.dirStack = QWidget()

        self.fileStackUI()
        self.dirStackUI()

        self.loadButton.clicked.connect(lambda: self._load_files_to_viewer(self.viewer))

        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.fileStack)
        self.Stack.addWidget(self.dirStack)

        zsliceHbox = QHBoxLayout()
        # zsliceHbox.addWidget(self.zsliceLbl)
        # zsliceHbox.addWidget(self.numZslices)

        totalVBox.addWidget(self.Stack)

        totalVBox.addLayout(zsliceHbox)
        totalVBox.addWidget(self.loadButton)
        # totalVBox.addWidget(self.save_as_gray_btn)
        # layout.addWidget(self.nextBtn)

    def save_as_grayscale(self, napari_viewer):
        images_to_import = []

        select_grayscale_directory = QFileDialog.getExistingDirectory(self, caption="Select the desired directory.")
        grayscale_output_directory = os.path.join(select_grayscale_directory, "grayscale")

        if self.file_radiobutton.isChecked():
            qListWidget = self.fileStack.findChild(QListWidget)
            images_to_import = [qListWidget.item(i).text() for i in range(qListWidget.count())]
        elif self.directory_radiobutton.isChecked():
            qLineEdit: QLineEdit = self.dirStack.findChild(QLineEdit)
            images_to_import = get_file_names(qLineEdit.text())
        print(images_to_import)

        loaded = load_image_from_file_as_nparray(images_to_import)

        for image in loaded:
            # image["image_data"] = to_grayscale_ndarray(image["image_data"])
            save_to_output_dir(image["image_data"], image["name"], grayscale_output_directory)
        msg = QMessageBox(QMessageBox.Information, "Save as grayscale", "Images saved as grayscale into the following directory: \n" + grayscale_output_directory + "\nConsider changing the input directory/files")
        msg.exec_()

    def _io_next(self, viewer):
        IOWidget = self.viewer.window._qt_window.findChild(QWidget, name="tseg: Input/Output")
        IOWidget.hide()
        PreWidget = self.viewer.window._qt_window.findChild(QWidget, name="tseg: Pre-Processing")
        PreWidget.show()
        # self.viewer.window.remove_dock_widget(InputOutputWidget(QWidget()))

    def _output_dir_changed(self, text):
        output_dir = text
        shared_config["output_dir"] = output_dir
        print(output_dir)

    def _load_files_to_viewer(self, napari_viewer):
        images_to_import = []
        if self.file_radiobutton.isChecked():
            qListWidget = self.fileStack.findChild(QListWidget)
            images_to_import = [qListWidget.item(i).text() for i in range(qListWidget.count())]
        elif self.directory_radiobutton.isChecked():
            # print("ischecked")
            qLineEdit: QLineEdit = self.dirStack.findChild(QLineEdit)
            # print("text is ", qLineEdit.text())
            images_to_import = get_file_names(qLineEdit.text())
            # print(images_to_import)
        # print('here')
        # print(images_to_import)
        loaded = load_image_from_file_as_nparray(images_to_import)
        load_images_to_viewer(napari_viewer, loaded, images_to_import)  # Pass the paths along with the images

        # print(loaded)

    def _file_radio_clicked(self):
        self.displayStack(0)

    def _dir_radio_clicked(self):
        self.displayStack(1)

    def fileStackUI(self):
        layout = QVBoxLayout()
        self.listOfFiles = QListWidget()
        self.browseFiles = QPushButton("Browse Files")
        self.browseFiles.setStyleSheet(TsegStyles.BTN_PRIMARY)
        self.browseFiles.clicked.connect(lambda: self._file_on_click(self.listOfFiles))
        layout.addWidget(self.listOfFiles)
        layout.addWidget(self.browseFiles)

        self.fileStack.setLayout(layout)

    def dirStackUI(self):
        layout = QVBoxLayout()

        self.dirLineEdit = QLineEdit(os.path.expanduser("~"))
        self.browseDir = QPushButton("Select Directory")
        self.browseDir.clicked.connect(lambda: self._dir_on_click(self.dirLineEdit))

        layout.addWidget(self.dirLineEdit)
        layout.addWidget(self.browseDir)
        self.dirStack.setLayout(layout)

    def displayStack(self, i):
        self.Stack.setCurrentIndex(i)

    def _file_on_click(self, fileListWidget: QListWidget):
        fileNames, _ = QFileDialog.getOpenFileNames(self, "Select one or more files to open", os.path.expanduser("~"), "Images (*.tif *.tiff *.png *.jpg)")

        # Clear and update the QListWidget with selected file paths
        fileListWidget.clear()
        for i, fileName in enumerate(fileNames):
            fileListWidget.insertItem(i, fileName)

        # Update shared_config with the list of file paths
        shared_config["selected_files"] = fileNames

        # Print for verification
        print("Updated shared_config['selected_files']:", shared_config["selected_files"])

    def _dir_on_click(self, dirLineEdit: QLineEdit):
        directory = QFileDialog.getExistingDirectory(self, caption="Select the desired directory.")
        dirLineEdit.setText(directory)
        self.Input_Directory = directory
        print(self.Input_Directory)
