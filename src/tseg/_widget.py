"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets

Replace code below according to your needs.
"""

from typing import TYPE_CHECKING
import tifffile
from .widgets.load_files import *
from .widgets.prep import *
from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from enum import Enum
import os


from .widgets.io_widget import InputOutputWidget
from .widgets.pre_widget import PreProcessingWidget
from .widgets.cnn_widget import CNNWidget
from .widgets.seg_widget import SegWidget
from .widgets.track_widget import TrackingWidget

from .config import *

if TYPE_CHECKING:
    import napari


print(output_dir)


# class InputOutputWidget(QWidget):
#     def __init__(self, napari_viewer):
#         super().__init__()
#         self.viewer = napari_viewer
#         self.Selected_Files = list()
#         self.Input_Directory = ""
#         self.file_radiobutton = QRadioButton("Select Files")
#         self.file_radiobutton.setChecked(True)
#         self.file_radiobutton.clicked.connect(self._file_radio_clicked)
#         self.directory_radiobutton = QRadioButton("Select Directory")
#         self.directory_radiobutton.clicked.connect(self._dir_radio_clicked)
#         radioHBox = QHBoxLayout()
#         radioHBox.addWidget(self.file_radiobutton)
#         radioHBox.addWidget(self.directory_radiobutton)

#         layout = QGridLayout(self)
#         inputGroupBox = QGroupBox(
#             "Input: Select files or a directory", checkable=False)
#         outputGroupBox = QGroupBox("Output: Specify the output folder name")
#         layout.addWidget(inputGroupBox)
#         totalVBox = QVBoxLayout()
#         outputForm = QFormLayout()
#         self.outputDirName = QLineEdit(os.path.join(
#             os.path.expanduser('~'), "tseg_output"))
#         self.outputDirName.textChanged.connect(
#             lambda: self._output_dir_changed(self.outputDirName.text()))
#         outputForm.addRow("Output directory path", self.outputDirName)
#         inputGroupBox.setLayout(totalVBox)
#         outputGroupBox.setLayout(outputForm)
#         # layout.addLayout(outputForm,0,1)
#         totalVBox.addLayout(radioHBox)
#         # totalVBox.addStretch()
#         layout.addWidget(outputGroupBox)

#         # self.zsliceLbl = QLabel("Number of Z-slices:")
#         # self.numZslices = QLineEdit()
#         self.loadButton = QPushButton("Load Files to the viewer")
#         self.loadButton.setStyleSheet("""
#                                    QPushButton{
#                                    background-color: #198754;
#                                    border-color: #28a745;
#                                    }
#                                    QPushButton::hover
#                                    {
#                                    background-color: #218838;
#                                    border-color: #1e7e34;
#                                    }
#                                    QPushButton::pressed
#                                    {
#                                    background-color: #1e7e34;
#                                    border-color: #1c7430;
#                                    }
#                                    """)
#         self.save_as_gray_btn = QPushButton("Save all as grayscale...")
#         self.save_as_gray_btn.clicked.connect(
#             lambda: self.save_as_grayscale(napari_viewer))

#         self.nextBtn = QPushButton("Next")
#         self.nextBtn.setStyleSheet("""
#                                    QPushButton{
#                                    background-color: #198754;
#                                    border-color: #28a745;
#                                    }
#                                    QPushButton::hover
#                                    {
#                                    background-color: #218838;
#                                    border-color: #1e7e34;
#                                    }
#                                    QPushButton::pressed
#                                    {
#                                    background-color: #1e7e34;
#                                    border-color: #1c7430;
#                                    }
#                                    """)

#         self.nextBtn.clicked.connect(self._io_next)
#         self.fileStack = QWidget()
#         self.dirStack = QWidget()

#         self.fileStackUI()
#         self.dirStackUI()

#         self.loadButton.clicked.connect(
#             lambda: self._load_files_to_viewer(self.viewer))

#         self.Stack = QStackedWidget(self)
#         self.Stack.addWidget(self.fileStack)
#         self.Stack.addWidget(self.dirStack)

#         zsliceHbox = QHBoxLayout()
#         # zsliceHbox.addWidget(self.zsliceLbl)
#         # zsliceHbox.addWidget(self.numZslices)

#         totalVBox.addWidget(self.Stack)

#         totalVBox.addLayout(zsliceHbox)
#         totalVBox.addWidget(self.loadButton)
#         totalVBox.addWidget(self.save_as_gray_btn)
#         # layout.addWidget(self.nextBtn)

#     def save_as_grayscale(self, napari_viewer):
#         images_to_import = []

#         select_grayscale_directory = QFileDialog.getExistingDirectory(
#             self, caption="Select the desired directory.")
#         grayscale_output_directory = os.path.join(
#             select_grayscale_directory, "grayscale")

#         if self.file_radiobutton.isChecked():
#             qListWidget: qListWidget = self.fileStack.findChild(
#                 QListWidget)
#             images_to_import = [qListWidget.item(
#                 i).text() for i in range(qListWidget.count())]
#         elif self.directory_radiobutton.isChecked():
#             qLineEdit: QLineEdit = self.dirStack.findChild(QLineEdit)
#             images_to_import = get_file_names(qLineEdit.text())
#         print(images_to_import)

#         loaded = load_image_from_file_as_nparray(images_to_import)

#         for image in loaded:
#             # image["image_data"] = to_grayscale_ndarray(image["image_data"])
#             save_to_output_dir(image["image_data"],
#                                image["name"], grayscale_output_directory)
#         msg = QMessageBox(QMessageBox.Information, "Save as grayscale", "Images saved as grayscale into the following directory: \n" +
#                           grayscale_output_directory+"\nConsider changing the input directory/files")
#         msg.exec_()

#     def _io_next(self, viewer):
#         IOWidget = self.viewer.window._qt_window.findChild(
#             QWidget, name="tseg: Input/Output")
#         IOWidget.hide()
#         PreWidget = self.viewer.window._qt_window.findChild(
#             QWidget, name="tseg: Pre-Processing")
#         PreWidget.show()
#         # self.viewer.window.remove_dock_widget(InputOutputWidget(QWidget()))

#     def _output_dir_changed(self, text):
#         output_dir = text
#         print(output_dir)

#     def _load_files_to_viewer(self, napari_viewer):
#         images_to_import = []
#         if self.file_radiobutton.isChecked():
#             qListWidget: qListWidget = self.fileStack.findChild(QListWidget)
#             images_to_import = [qListWidget.item(
#                 i).text() for i in range(qListWidget.count())]
#         elif self.directory_radiobutton.isChecked():
#             # print("ischecked")
#             qLineEdit: QLineEdit = self.dirStack.findChild(QLineEdit)
#             # print("text is ", qLineEdit.text())
#             images_to_import = get_file_names(qLineEdit.text())
#             # print(images_to_import)
#         # print('here')
#         # print(images_to_import)
#         loaded = load_image_from_file_as_nparray(images_to_import)
#         load_images_to_viewer(napari_viewer, loaded)

#         # print(loaded)

#     def _file_radio_clicked(self):
#         self.displayStack(0)

#     def _dir_radio_clicked(self):
#         self.displayStack(1)

#     def fileStackUI(self):
#         layout = QHBoxLayout()
#         self.listOfFiles = QListWidget()
#         self.browseFiles = QPushButton("Select Files")
#         self.browseFiles.clicked.connect(
#             lambda: self._file_on_click(self.listOfFiles))
#         layout.addWidget(self.listOfFiles)
#         layout.addWidget(self.browseFiles)

#         self.fileStack.setLayout(layout)

#     def dirStackUI(self):
#         layout = QHBoxLayout()

#         self.dirLineEdit = QLineEdit(os.path.expanduser('~'))
#         self.browseDir = QPushButton("Select Directory")
#         self.browseDir.clicked.connect(
#             lambda: self._dir_on_click(self.dirLineEdit))

#         layout.addWidget(self.dirLineEdit)
#         layout.addWidget(self.browseDir)
#         self.dirStack.setLayout(layout)

#     def displayStack(self, i):
#         self.Stack.setCurrentIndex(i)

#     def _file_on_click(self, fileListWidget: QListWidget):
#         fileNames, _ = QFileDialog.getOpenFileNames(
#             self, "select one or more files to open", os.path.expanduser('~'), "Images (*.tif *.tiff)")
#         # print(files)
#         # self.Selected_Files = files
#         # for item in self.Selected_Files:
#         #     print(os.path.basename(item))
#         fileListWidget.clear()
#         for i, fileName in enumerate(fileNames):
#             fileListWidget.insertItem(i, fileName)

#             # fileListWidget.insertItem(i, fileName.split('/')[-1])

#     def _dir_on_click(self, dirLineEdit: QLineEdit):
#         directory = QFileDialog.getExistingDirectory(
#             self, caption="Select the desired directory.")
#         dirLineEdit.setText(directory)
#         self.Input_Directory = directory
#         print(self.Input_Directory)
