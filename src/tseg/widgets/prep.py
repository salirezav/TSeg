import cv2
import numpy as np

def adaptive_thresh(img, sub_region, c_value):
    print("subregion:", sub_region, "c_val", c_value)
    # Convert image to 8-bit single-channel
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
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

def min_max_normalization(image):
    norm_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    return norm_image.astype(np.uint8)

def scale_to_minus1_plus1(image):
    norm_image = cv2.normalize(image, None, -1, 1, cv2.NORM_MINMAX)
    return norm_image

def z_score_normalization(image):
    mean, std = cv2.meanStdDev(image)
    norm_image = (image - mean[0][0]) / std[0][0]
    norm_image = cv2.normalize(norm_image, None, 0, 255, cv2.NORM_MINMAX)
    return norm_image.astype(np.uint8)

def histogram_equalization(image):
    # Convert image to 8-bit single-channel
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if len(image.shape) == 2:  # Grayscale image
        norm_image = cv2.equalizeHist(image)
    else:  # Color image
        norm_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        norm_image[:, :, 0] = cv2.equalizeHist(norm_image[:, :, 0])
        norm_image = cv2.cvtColor(norm_image, cv2.COLOR_YCrCb2BGR)
    return norm_image

def gamma_correction(image, gamma=1.0):
    # Convert image to 8-bit single-channel
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    norm_image = cv2.LUT(image, table)
    return norm_image

def convert_to_grayscale(image):
    if len(image.shape) == 2:  # Already grayscale
        return image
    elif len(image.shape) == 3 and image.shape[2] == 3:  # RGB image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] == 4:  # RGBA image
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else:
        raise ValueError("Unsupported image format for grayscale conversion")

def apply_contrast_limit(image, min_val, max_val):
    norm_image = cv2.normalize(image, None, min_val, max_val, cv2.NORM_MINMAX)
    return norm_image.astype(np.uint8)
