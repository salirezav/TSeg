from PIL import Image
import tifffile
import numpy as np
import os
import cv2
import glob

rgb_weights = [0.2989, 0.5870, 0.1140]


def create_dir_if_not_exist(directory):
    # Creates the output directory if it does not exist
    if not os.path.isdir(f'{os.getcwd()}/{directory}'):
        os.makedirs(f'{os.getcwd()}/{directory}')


def load_image_from_file_as_nparray(file_names) -> list():
    images = [{"name": os.path.basename(file), "image_data": cv2.imread(file, cv2.IMREAD_GRAYSCALE)}
              for file in file_names]
    # all_images_nparray = np.asarray(images)
    return images


def to_grayscale(image_path):
    img = Image.open(image_path).convert('L')
    new_path = image_path.split("\\")[1]
    img.save(f"{PRE_PROCESS_OUT_DIR}/{new_path}")


def get_file_names(directory) -> list():
    # Gets all file names in the input directory and sorts them by name
    # for file in os.listdir(directory):
    # check only text files
    # if file.endswith('.tif'):
    # print(file)
    # yield os.path.join(directory, file)
    file_names = glob.glob(f'{directory}/*.tif*')
    file_names = sorted(file_names)
    # print(file_names)
    return file_names


def load_images_to_viewer(napari_viewer, images_to_import):
    for image in images_to_import:
        napari_viewer.add_image(
            image["image_data"], name=image["name"])


def to_grayscale_ndarray(image):
    return np.dot(image[..., :3], rgb_weights)


def save_to_output_dir(image_nd, img_name, out_dir):
    print("out_dir: ", out_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    cv2.imwrite(os.path.join(out_dir, img_name), image_nd)
