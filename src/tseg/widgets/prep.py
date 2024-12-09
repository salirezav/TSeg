import cv2
import numpy as np


def adaptive_thresh(img, sub_region, c_value):
    print("subregion:", sub_region, "c_val", c_value)
    thresh = cv2.adaptiveThreshold(img, 255,
                                   cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, sub_region, c_value)
    return thresh


def log_transformation(image):

    # Apply log transformation method
    c = 255 / np.log(1 + np.max(image))
    log_image = c * (np.log(image + 1))

    # Specify the data type so that
    # float value will be converted to int
    log_image = np.array(log_image, dtype=np.uint8)
    return log_image
