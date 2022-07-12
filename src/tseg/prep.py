import cv2


def adaptive_thresh(img, sub_region, c_value):
    print("subregion:", sub_region, "c_val", c_value)
    thresh = cv2.adaptiveThreshold(img, 255,
                                   cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, sub_region, c_value)
    return thresh


