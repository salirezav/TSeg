from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from tseg.config import shared_config, TsegStyles  # Import shared_config
import numpy as np  # Import numpy as np
from scipy.ndimage import center_of_mass  # Import center_of_mass
from tqdm import tqdm  # Import tqdm
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
from napari.layers import Points


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
        ccLabel = QLabel("Connected Component")
        ccLabel.setAlignment(Qt.AlignLeft)
        ccLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(ccLabel)

        ccImageLabel = QLabel("Original Data")
        layout.addWidget(ccImageLabel)
        self.ccImageDD = QComboBox(self)
        _populate_image_dropdown(self.ccImageDD)
        layout.addWidget(self.ccImageDD)

        self.ccButton = QPushButton("Calculate")
        self.ccButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.ccButton.clicked.connect(self.calculate_connected_component)
        layout.addWidget(self.ccButton)

        # Noise Removal Section
        noiseRemovalLabel = QLabel("Noise Removal")
        noiseRemovalLabel.setAlignment(Qt.AlignLeft)
        noiseRemovalLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(noiseRemovalLabel)

        nrImageLabel = QLabel("Original Data")
        layout.addWidget(nrImageLabel)
        self.nrImageDD = QComboBox(self)
        _populate_image_dropdown(self.nrImageDD)
        layout.addWidget(self.nrImageDD)

        nrLabeledLabel = QLabel("Labeled Data")
        layout.addWidget(nrLabeledLabel)
        self.nrLabeledDD = QComboBox(self)
        _populate_image_dropdown(self.nrLabeledDD)
        layout.addWidget(self.nrLabeledDD)

        self.volThresholdSpinBox = QSpinBox()
        self.volThresholdSpinBox.setRange(1, 100)
        self.volThresholdSpinBox.setValue(2)
        layout.addWidget(self.volThresholdSpinBox)

        self.noiseRemovalButton = QPushButton("Remove Noise")
        self.noiseRemovalButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.noiseRemovalButton.clicked.connect(self.remove_noise)
        layout.addWidget(self.noiseRemovalButton)

        # Center Detection Section
        centerDetectionLabel = QLabel("Center Detection")
        centerDetectionLabel.setAlignment(Qt.AlignLeft)
        centerDetectionLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(centerDetectionLabel)

        cdImageLabel = QLabel("Original Data")
        layout.addWidget(cdImageLabel)
        self.cdImageDD = QComboBox(self)
        _populate_image_dropdown(self.cdImageDD)
        layout.addWidget(self.cdImageDD)

        cdLabeledLabel = QLabel("Labeled Data")
        layout.addWidget(cdLabeledLabel)
        self.cdLabeledDD = QComboBox(self)
        _populate_image_dropdown(self.cdLabeledDD)
        layout.addWidget(self.cdLabeledDD)

        self.centerDetectionButton = QPushButton("Detect Centers")
        self.centerDetectionButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.centerDetectionButton.clicked.connect(self.detect_centers)
        layout.addWidget(self.centerDetectionButton)

        # Track Section
        trackLabel = QLabel("Track")
        trackLabel.setAlignment(Qt.AlignLeft)
        trackLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(trackLabel)

        trackCentersLabel = QLabel("Centers Data")
        layout.addWidget(trackCentersLabel)
        self.trackCentersDD = QComboBox(self)
        _populate_image_dropdown(self.trackCentersDD)
        layout.addWidget(self.trackCentersDD)

        self.trackButton = QPushButton("Track")
        self.trackButton.setStyleSheet(TsegStyles.BTN_GREEN)
        self.trackButton.clicked.connect(self.track)
        layout.addWidget(self.trackButton)

        # Connect layer events to update dropdowns
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.ccImageDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.ccImageDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.ccImageDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.nrImageDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.nrImageDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.nrImageDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.nrLabeledDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.nrLabeledDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.nrLabeledDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.cdImageDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.cdImageDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.cdImageDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.cdLabeledDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.cdLabeledDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.cdLabeledDD))
        self.viewer.layers.events.inserted.connect(lambda event: _populate_image_dropdown(self.trackCentersDD))
        self.viewer.layers.events.removed.connect(lambda event: _populate_image_dropdown(self.trackCentersDD))
        self.viewer.layers.events.changed.connect(lambda event: _populate_image_dropdown(self.trackCentersDD))

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

        self.viewer.add_image(centers_array, name=f"{selected_image}_centers")

    def track(self):
        selected_centers = self.trackCentersDD.currentText()
        if selected_centers == "-select image-":
            print("No centers data selected!")
            return

        centers_layer = self.viewer.layers[selected_centers]
        centers_data = centers_layer.data
        xx, yy, zz = tracker(centers_data)
        self.visualize_tracking(xx, yy, zz)

    def visualize_tracking(self, xx, yy, zz):
        points = []
        for i in range(len(xx)):
            for j in range(len(xx[i])):
                points.append([zz[i][j], xx[i][j], yy[i][j]])

        points_layer = Points(points, name="Tracked Points", size=1, face_color="red", edge_color="white")
        self.viewer.add_layer(points_layer)


def ccl_3d(all_image_arr):
    """
    First we extract the labels of the components for all the cells
    across all the frames. Thus the number of components and their labels
    are discovered here:
    """
    import numpy as np
    from scipy.ndimage import label
    from tqdm import tqdm

    all_image_arr = np.asarray(all_image_arr)
    structure = np.ones((3, 3, 3), dtype=int)
    all_labeled = np.zeros(shape=all_image_arr.shape)
    all_ncomponents = np.zeros(all_image_arr.shape[0])

    for frames in tqdm(range(all_image_arr.shape[0]), desc="3D Connected Component Calculation"):
        all_labeled[frames], all_ncomponents[frames] = label(all_image_arr[frames], structure)

    return all_labeled, all_ncomponents


def noise_removal(all_img_arr, all_labeled, vol_threshold=1):
    """
    For Removing the noise,, i've considered only the components with
    the volume greater tha 1 pixel. Thus first I computed the volume of
    each component and then extracted the centers only for the components
    with the volume greater than 1 pixels:
    """
    all_img_arr = np.asarray(all_img_arr)

    unique = list()
    counts = list()
    for frames in range(all_img_arr.shape[0]):
        unq = np.unique(all_labeled[frames], return_counts=True)
        unique.append(unq[0])
        counts.append(unq[1])

    # Here I'm selecting only the center of the components with the volume
    # less than 1 pixel and put them in thr_idxs list  :

    thr_idxs = [[]]
    for i in tqdm(range(len(counts)), desc=f"Selecting volumes > {vol_threshold}"):
        for j in range(1, len(counts[i])):
            if counts[i][j] > vol_threshold:
                thr_idxs[i].append(unique[i][j])
        thr_idxs.append([])
    thr_idxs = [pick for pick in thr_idxs if len(pick) > 0]

    return thr_idxs


def center_detection(all_img_arr, all_labeled, thr_idxs):
    all_img_arr = np.asarray(all_img_arr)

    all_centers_noisefree = []
    for frames in tqdm(range(all_img_arr.shape[0]), desc="Detecting the center of components."):
        all_centers_noisefree.append(center_of_mass(all_img_arr[frames], labels=all_labeled[frames], index=thr_idxs[frames]))

    return all_centers_noisefree


def tracker(all_centers):
    all_cen = all_centers
    new_objects = [[(0, x)] for x in all_centers[0]]

    t_limit = 20

    for i in tqdm(range(1, len(all_cen) - 1), desc="Tracking..."):
        current_frame = all_cen[i]
        last_known_centers = [obj[-1][1] for obj in new_objects if len(obj) > 0]
        cost = distance.cdist(last_known_centers, current_frame, "euclidean")
        obj_ids, new_centers_ind = linear_sum_assignment(cost)

        all_center_inds = set(range(len(current_frame)))

        for obj_id, new_center_ind in zip(obj_ids, new_centers_ind):
            if (
                distance.euclidean(
                    np.array(current_frame[new_center_ind]),
                    np.array(new_objects[obj_id][-1][1]),
                )
                <= t_limit
            ):
                all_center_inds.remove(new_center_ind)
                new_objects[obj_id].append((i, current_frame[new_center_ind]))

        for new_center_ind in all_center_inds:
            new_objects.append([(i, current_frame[new_center_ind])])
    xx = [[]]
    yy = [[]]
    zz = [[]]
    for i in range(len(new_objects)):
        for j in range(len(new_objects[i])):
            zz[i].append(new_objects[i][j][1][0])
            xx[i].append(new_objects[i][j][1][1])
            yy[i].append(new_objects[i][j][1][2])
        xx.append([])
        zz.append([])
        yy.append([])

    zz = [pick for pick in zz if len(pick) > 0]
    xx = [pick for pick in xx if len(pick) > 0]
    yy = [pick for pick in yy if len(pick) > 0]

    return (xx, yy, zz)
