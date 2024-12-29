from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from tseg.config import shared_config  # Import shared_config
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

        # Connected Component Section
        ccLabel = QLabel("Connected Component")
        ccLabel.setAlignment(Qt.AlignLeft)
        ccLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(ccLabel)

        self.ccButton = QPushButton("Calculate")
        self.ccButton.setStyleSheet(
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
        self.ccButton.clicked.connect(self.calculate_connected_component)
        layout.addWidget(self.ccButton)

        # Noise Removal Section
        noiseRemovalLabel = QLabel("Noise Removal")
        noiseRemovalLabel.setAlignment(Qt.AlignLeft)
        noiseRemovalLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(noiseRemovalLabel)

        self.volThresholdSpinBox = QSpinBox()
        self.volThresholdSpinBox.setRange(1, 100)
        self.volThresholdSpinBox.setValue(2)
        layout.addWidget(self.volThresholdSpinBox)

        self.noiseRemovalButton = QPushButton("Remove Noise")
        self.noiseRemovalButton.setStyleSheet(
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
        self.noiseRemovalButton.clicked.connect(self.remove_noise)
        layout.addWidget(self.noiseRemovalButton)

        # Center Detection Section
        centerDetectionLabel = QLabel("Center Detection")
        centerDetectionLabel.setAlignment(Qt.AlignLeft)
        centerDetectionLabel.setStyleSheet("font-weight: bold; font-size: 18pt;")
        layout.addWidget(centerDetectionLabel)

        self.centerDetectionButton = QPushButton("Detect Centers")
        self.centerDetectionButton.setStyleSheet(
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
        self.centerDetectionButton.clicked.connect(self.detect_centers)
        layout.addWidget(self.centerDetectionButton)

    def calculate_connected_component(self):
        selected_layer = self.viewer.layers.selection.active
        if selected_layer is not None:
            img_data = selected_layer.data
            labeled, ncomponents = ccl_3d(img_data)
            self.viewer.add_image(labeled.astype(np.uint8), name=f"{selected_layer.name}_labeled")
            print(f"Number of components: {ncomponents}")

    def remove_noise(self):
        selected_layer = self.viewer.layers.selection.active
        if selected_layer is not None:
            img_data = selected_layer.data
            labeled, _ = ccl_3d(img_data)
            vol_threshold = self.volThresholdSpinBox.value()
            thr_idxs = noise_removal(img_data, labeled, vol_threshold)
            # print(f"Threshold indices: {thr_idxs}")

    def detect_centers(self):
        selected_layer = self.viewer.layers.selection.active
        if selected_layer is not None:
            img_data = selected_layer.data
            labeled, _ = ccl_3d(img_data)
            vol_threshold = self.volThresholdSpinBox.value()
            thr_idxs = noise_removal(img_data, labeled, vol_threshold)
            all_centers_noisefree = center_detection(img_data, labeled, thr_idxs)
            # print(f"Centers: {all_centers_noisefree}")

            # Create an array of the same shape as the input for visualization
            centers_array = np.zeros_like(img_data, dtype=np.uint8)
            for t, centers in enumerate(all_centers_noisefree):
                for center in centers:
                    z, x, y = map(int, center)
                    centers_array[t, z, x, y] = 1

            self.viewer.add_image(centers_array, name=f"{selected_layer.name}_centers")

            # Perform tracking
            xx, yy, zz = tracker(all_centers_noisefree)
            # print(f"Tracking results: xx={xx}, yy={yy}, zz={zz}")

            # Visualize tracking results
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
