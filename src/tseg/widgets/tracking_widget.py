from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from tseg.config import shared_config, TsegStyles  # Import shared_config
import numpy as np  # Import numpy as np
from napari.layers import Points
import pandas as pd  # Import pandas for DataFrame manipulation
from tseg.core.tracking import ccl_3d, noise_removal, center_detection, tracker, preprocessing_for_clustering, computing_affinity, clustering, visualize_clusters  # Import functions from tracking.py


class TrackingWidget(QWidget):

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QVBoxLayout(self)

        def _populate_image_dropdown(dropdown):
            dropdown.clear()
            dropdown.addItem("-select image-")
            image_names = [layer.name for layer in self.viewer.layers if layer._type_string == "image"]
            dropdown.addItems(image_names)

        # Connected Component Section
        ccFormLayout = QFormLayout()
        ccLabel = QLabel("Connected Component Labeling")
        ccLabel.setAlignment(Qt.AlignLeft)
        ccLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(ccLabel)

        self.ccImageDD = QComboBox(self)
        _populate_image_dropdown(self.ccImageDD)
        ccFormLayout.addRow("Original Data", self.ccImageDD)

        self.ccButton = QPushButton("Calculate")
        self.ccButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.ccButton.clicked.connect(self.calculate_connected_component)
        ccFormLayout.addRow(self.ccButton)
        layout.addLayout(ccFormLayout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        line = QHLine()
        line.setStyleSheet("color: white; background-color: white; height: 2px;")
        layout.addWidget(line)  # Add horizontal line
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Noise Removal Section
        nrFormLayout = QFormLayout()
        noiseRemovalLabel = QLabel("Noise Removal")
        noiseRemovalLabel.setAlignment(Qt.AlignLeft)
        noiseRemovalLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(noiseRemovalLabel)

        self.nrImageDD = QComboBox(self)
        _populate_image_dropdown(self.nrImageDD)
        nrFormLayout.addRow("Original Data", self.nrImageDD)

        self.nrLabeledDD = QComboBox(self)
        _populate_image_dropdown(self.nrLabeledDD)
        nrFormLayout.addRow("Labeled Data", self.nrLabeledDD)

        self.volThresholdSpinBox = QSpinBox()
        self.volThresholdSpinBox.setRange(1, 100)
        self.volThresholdSpinBox.setValue(2)
        nrFormLayout.addRow("Volume Threshold", self.volThresholdSpinBox)

        self.noiseRemovalButton = QPushButton("Remove Noise")
        self.noiseRemovalButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.noiseRemovalButton.clicked.connect(self.remove_noise)
        nrFormLayout.addRow(self.noiseRemovalButton)
        layout.addLayout(nrFormLayout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        line = QHLine()
        line.setStyleSheet("color: white; background-color: white; height: 2px;")
        layout.addWidget(line)  # Add horizontal line
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Center Detection Section
        cdFormLayout = QFormLayout()
        centerDetectionLabel = QLabel("Center Detection")
        centerDetectionLabel.setAlignment(Qt.AlignLeft)
        centerDetectionLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(centerDetectionLabel)

        self.cdImageDD = QComboBox(self)
        _populate_image_dropdown(self.cdImageDD)
        cdFormLayout.addRow("Original Data", self.cdImageDD)

        self.cdLabeledDD = QComboBox(self)
        _populate_image_dropdown(self.cdLabeledDD)
        cdFormLayout.addRow("Labeled Data", self.cdLabeledDD)

        self.centerDetectionButton = QPushButton("Detect Centers")
        self.centerDetectionButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.centerDetectionButton.clicked.connect(self.detect_centers)
        cdFormLayout.addRow(self.centerDetectionButton)
        layout.addLayout(cdFormLayout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        line = QHLine()
        line.setStyleSheet("color: white; background-color: white; height: 2px;")
        layout.addWidget(line)  # Add horizontal line
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Track Section
        trackFormLayout = QFormLayout()
        trackLabel = QLabel("Tracking")
        trackLabel.setAlignment(Qt.AlignLeft)
        trackLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(trackLabel)

        self.trackCentersDD = QComboBox(self)
        _populate_image_dropdown(self.trackCentersDD)
        trackFormLayout.addRow("Centers Data", self.trackCentersDD)

        self.trackButton = QPushButton("Track")
        self.trackButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.trackButton.clicked.connect(self.track)
        trackFormLayout.addRow(self.trackButton)
        layout.addLayout(trackFormLayout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        line = QHLine()
        line.setStyleSheet("color: white; background-color: white; height: 2px;")
        layout.addWidget(line)  # Add horizontal line
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Clustering Section
        clusteringFormLayout = QFormLayout()
        clusteringLabel = QLabel("Clustering Trajectories")
        clusteringLabel.setAlignment(Qt.AlignLeft)
        clusteringLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(clusteringLabel)

        self.clusterCentersDD = QComboBox(self)
        _populate_image_dropdown(self.clusterCentersDD)
        clusteringFormLayout.addRow("Centers Data", self.clusterCentersDD)

        self.arOrderSpinBox = QSpinBox()
        self.arOrderSpinBox.setRange(1, 10)
        self.arOrderSpinBox.setValue(5)
        clusteringFormLayout.addRow("Number of Autoregressive Orders", self.arOrderSpinBox)

        self.clusterNumSpinBox = QSpinBox()
        self.clusterNumSpinBox.setRange(1, 10)
        self.clusterNumSpinBox.setValue(3)
        clusteringFormLayout.addRow("Number of Clusters", self.clusterNumSpinBox)

        self.clusterButton = QPushButton("Cluster Trajectories")
        self.clusterButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.clusterButton.clicked.connect(self.cluster_trajectories)
        clusteringFormLayout.addRow(self.clusterButton)
        layout.addLayout(clusteringFormLayout)

        # Connect layer events to update dropdowns
        dropdowns = [
            self.ccImageDD, self.nrImageDD, self.nrLabeledDD, self.cdImageDD,
            self.cdLabeledDD, self.trackCentersDD, self.clusterCentersDD
        ]

        for dropdown in dropdowns:
            self.viewer.layers.events.inserted.connect(lambda event, dd=dropdown: _populate_image_dropdown(dd))
            self.viewer.layers.events.removed.connect(lambda event, dd=dropdown: _populate_image_dropdown(dd))
            self.viewer.layers.events.changed.connect(lambda event, dd=dropdown: _populate_image_dropdown(dd))

    def calculate_connected_component(self):
        selected_image = self.ccImageDD.currentText()
        if selected_image == "-select image-":
            print("No image selected!")
            return

        selected_layer = self.viewer.layers[selected_image]
        img_data = selected_layer.data
        labeled, ncomponents = ccl_3d(img_data)
        self.viewer.add_image(labeled.astype(np.uint8), name=f"{selected_layer.name}_labeled")
        print(f"Number of components: {ncomponents}")

    def remove_noise(self):
        selected_image = self.nrImageDD.currentText()
        selected_labeled = self.nrLabeledDD.currentText()
        if selected_image == "-select image-" or selected_labeled == "-select image-":
            print("No image or labeled data selected!")
            return

        img_data = self.viewer.layers[selected_image].data
        labeled = self.viewer.layers[selected_labeled].data
        vol_threshold = self.volThresholdSpinBox.value()
        thr_idxs = noise_removal(img_data, labeled, vol_threshold)
        self.viewer.layers[selected_labeled].metadata["thr_idxs"] = thr_idxs

    def detect_centers(self):
        selected_image = self.cdImageDD.currentText()
        selected_labeled = self.cdLabeledDD.currentText()
        if selected_image == "-select image-" or selected_labeled == "-select image-":
            print("No image or labeled data selected!")
            return

        img_data = self.viewer.layers[selected_image].data
        labeled = self.viewer.layers[selected_labeled].data
        thr_idxs = self.viewer.layers[selected_labeled].metadata.get("thr_idxs", [])
        all_centers_noisefree = center_detection(img_data, labeled, thr_idxs)

        centers_array = np.zeros_like(img_data, dtype=np.uint8)
        for t, centers in enumerate(all_centers_noisefree):
            for center in centers:
                z, x, y = map(int, center)
                centers_array[t, z, x, y] = 1

        centers_layer = self.viewer.add_image(centers_array, name=f"{selected_image}_centers")
        centers_layer.metadata["all_centers_noisefree"] = all_centers_noisefree

    def track(self):
        selected_centers = self.trackCentersDD.currentText()
        if selected_centers == "-select image-":
            print("No centers data selected!")
            return

        centers_layer = self.viewer.layers[selected_centers]
        all_centers_noisefree = centers_layer.metadata.get("all_centers_noisefree", [])
        if not all_centers_noisefree:
            print("No center data found in metadata!")
            return

        xx, yy, zz = tracker(all_centers_noisefree)
        self.visualize_tracking(xx, yy, zz)

    def visualize_tracking(self, xx, yy, zz):
        points = []
        for i in range(len(xx)):
            for j in range(len(xx[i])):
                points.append([zz[i][j], xx[i][j], yy[i][j]])

        points_layer = Points(points, name="Tracked Points", size=1, face_color="red", edge_color="white")
        self.viewer.add_layer(points_layer)

    def cluster_trajectories(self):
        ar_order = self.arOrderSpinBox.value()
        cluster_num = self.clusterNumSpinBox.value()

        selected_centers = self.clusterCentersDD.currentText()
        if selected_centers == "-select image-":
            print("No centers data selected!")
            return

        centers_layer = self.viewer.layers[selected_centers]
        all_centers_noisefree = centers_layer.metadata.get("all_centers_noisefree", [])
        if not all_centers_noisefree:
            print("No center data found in metadata!")
            return

        xx, yy, zz = tracker(all_centers_noisefree)

        # Pre Processing for clustering
        tracked_frames = len(all_centers_noisefree) - 1
        object_numbers = len(xx)
        xx, yy, zz = preprocessing_for_clustering(xx, yy, zz, tracked_frames, object_numbers)

        # Setting Auto regressive parameters and other initializations
        number_of_points = np.shape(xx)[0]
        columns = ar_order * 2 * 2
        flatten_AR_mat = np.zeros(shape=(number_of_points, columns))
        print((number_of_points, columns), flatten_AR_mat.shape)

        # Creating a pool of preprocessed trajectories
        traj_pool = np.stack([xx, yy, zz])
        print(traj_pool.shape, len(xx))

        # Computing the affinity matrix for clustering
        sim1, sim2, [A1, A2, A3, A4, A5], (X, C) = computing_affinity(traj_pool, tracked_frames, flatten_AR_mat, number_of_points)

        # Perform clustering
        labels = clustering(sim1, cluster_num, "labels.npy", "affinity.npy")

        # Visualize clusters in Napari
        self.visualize_clusters_in_napari(xx, yy, zz, labels, cluster_num)

        print(f"Clustering with AR order: {ar_order} and number of clusters: {cluster_num}")

    def visualize_clusters_in_napari(self, xx, yy, zz, labels, cluster_num):
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'white', 'orange', 'purple', 'brown']
        for cluster_id in range(cluster_num):
            cluster_points = []
            for i in range(len(xx)):
                if labels[i] == cluster_id:
                    for j in range(len(xx[i])):
                        cluster_points.append([zz[i][j], xx[i][j], yy[i][j]])
            points_layer = Points(cluster_points, name=f"Cluster {cluster_id + 1}", size=1, face_color=colors[cluster_id % len(colors)], edge_color="white")
            self.viewer.add_layer(points_layer)


class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
