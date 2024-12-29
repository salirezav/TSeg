import cv2
import numpy as np

def detect_data_format(image):
    shape = image.shape
    if len(shape) == 2:
        return "2D"
    elif len(shape) == 3:
        if shape[0] in [1, 3, 4]:
            return "2D with channels"
        else:
            return "3D"
    elif len(shape) == 4:
        if shape[1] in [1, 3, 4]:
            return "3D with channels"
        else:
            return "4D"
    elif len(shape) == 5:
        return "4D with channels"
    else:
        raise ValueError("Unsupported image format")

def preprocess_image(image, operation, **kwargs):
    data_format = detect_data_format(image)
    
    if data_format == "2D":
        return operation(image, **kwargs)
    elif data_format == "2D with channels":
        channels = [operation(image[c], **kwargs) for c in range(image.shape[0])]
        return np.stack(channels, axis=0)
    elif data_format == "3D":
        slices = [operation(image[z], **kwargs) for z in range(image.shape[0])]
        return np.stack(slices, axis=0)
    elif data_format == "3D with channels":
        channels = []
        for c in range(image.shape[0]):
            slices = [operation(image[c, z], **kwargs) for z in range(image.shape[1])]
            channels.append(np.stack(slices, axis=0))
        return np.stack(channels, axis=0)
    elif data_format == "4D":
        timepoints = []
        for t in range(image.shape[0]):
            slices = [operation(image[t, z], **kwargs) for z in range(image.shape[1])]
            timepoints.append(np.stack(slices, axis=0))
        return np.stack(timepoints, axis=0)
    elif data_format == "4D with channels":
        channels = []
        for c in range(image.shape[0]):
            timepoints = []
            for t in range(image.shape[1]):
                slices = [operation(image[c, t, z], **kwargs) for z in range(image.shape[2])]
                timepoints.append(np.stack(slices, axis=0))
            channels.append(np.stack(timepoints, axis=0))
        return np.stack(channels, axis=0)
    else:
        raise ValueError("Unsupported image format")

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
