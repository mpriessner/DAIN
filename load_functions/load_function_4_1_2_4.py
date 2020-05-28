import os
from aicsimageio import AICSImage, imread
import shutil
import time
import numpy
import random
from aicsimageio import AICSImage, imread
from aicsimageio.writers import png_writer 
import numpy as np
from tqdm import tqdm
from google.colab.patches import cv2_imshow
from aicsimageio.writers.ome_tiff_writer import OmeTiffWriter
from tqdm import tqdm
from timeit import default_timer as timer
import imageio
import tifffile 
from aicsimageio.transforms import reshape_data

def create_3D_image(img, x_dim, y_dim):
# creates 3D image with 3 times the same values for RGB because the NN was generated for normal rgb images dim(3,x,y)
  image_3D = np.zeros((3,y_dim,x_dim))
  image_3D[0] = img
  image_3D[1] = img
  image_3D[2] = img
  # print(image_3D.shape)
  return image_3D


# create supporting functions
def get_file_list(filepath):
  # get path of files into a list
  folder_path = filepath
  flist = os.listdir(folder_path)
  file_list = []
  for i in flist:
    file_path = os.path.join(folder_path, i)
    file_list.append(file_path)
  file_list.sort()
  return file_list
# filepath = "/content/drive/My Drive/Colab Notebooks/Resulution_enhancement/Test_image"
# filepath_list = get_file_list(filepath)

def convert(img, target_type_min, target_type_max, target_type):
  # this function converts images from float32 to unit8 
    imin = img.min()
    imax = img.max()
    a = (target_type_max - target_type_min) / (imax - imin)
    b = target_type_max - a * imax
    new_img = (a * img + b).astype(target_type)
    return new_img


#create the folder system for storing all the folders and files
def create_foldersystem(root, folder_name):
  os.chdir(root)
  destination = os.path.join(root,folder_name)
  destination_gt = destination + "_gt"
  # remove folder if there was one before
  # create new folder
  if os.path.exists(destination):
    shutil.rmtree(destination)
    os.mkdir(destination)
  else:
    os.mkdir(destination)

  if os.path.exists(destination_gt):
    shutil.rmtree(destination_gt)
    os.mkdir(destination_gt)
  else:
    os.mkdir(destination_gt)  
  return destination, destination_gt


def run_code(filepath_list, destination, destination_gt, i, t, images_jump):
  # create virtual number of files
    print(filepath_list[i])
    txt_name_log = open(destination + "/name_log.txt", "a")
    txt_name_log.write("{}, {}\n".format(("%03d" %(t)+"-" +"%03d"  %(i)), filepath_list[i]))
    txt_name_log.close()

    img = AICSImage(filepath_list[i])
    z_dim = img.shape[2]

    #dim for later for generating the image_3d files
    x_dim = img.shape[-2]
    y_dim = img.shape[-1]

    for j in range((z_dim//images_jump)-1):
      #create new directory-path
      file_folder = ("%03d" %(t)+"-" +"%03d"  %(i) + "-"+"%03d" %(j))

      os.chdir(destination_gt)
      os.mkdir(file_folder)
      GT_path_2 = os.path.join(destination_gt, file_folder)

      os.chdir(destination)
      os.mkdir(file_folder)
      new_folder_path_2 = os.path.join(destination, file_folder)
      os.chdir(new_folder_path_2)

      #here put the image pngs into the folder (instead of creating the folder)
      #convert image to unit8 otherwise warning
      first = j* images_jump
      second = j*images_jump+images_jump
      if second <= z_dim-1: #*images_jump-images_jump:
        img_1 = img.get_image_data("YX", S=0, T=0, Z=0, C=first)
        img_1 = create_3D_image(img_1, x_dim, y_dim)
        img_1 = convert(img_1, 0, 255, np.uint8)

        img_2 = img.get_image_data("YX", S=0, T=0, Z=0, C=second)
        img_2 = create_3D_image(img_2, x_dim, y_dim)
        img_2 = convert(img_2, 0, 255, np.uint8)

        img_mid = img.get_image_data("YX", S=0, T=0, Z=0, C=first+1)
        img_mid = create_3D_image(img_mid, x_dim, y_dim)
        img_mid = convert(img_mid, 0, 255, np.uint8)
        if images_jump ==3:
            img_mid2 = img.get_image_data("YX", S=0, T=0, Z=0, C=first+2)
            img_mid2 = create_3D_image(img_mid2, x_dim, y_dim)
            img_mid2 = convert(img_mid2, 0, 255, np.uint8)


        # saving images as PNG
        with png_writer.PngWriter("im1.png") as writer1:
          writer1.save(img_1)
        with png_writer.PngWriter("im3.png") as writer2:
          writer2.save(img_2)

        os.chdir(GT_path_2)
        with png_writer.PngWriter("im2.png") as writer2:
          writer2.save(img_mid)

        if images_jump ==3:
          with png_writer.PngWriter("im2.2.png") as writer2:
            writer2.save(img_mid2)
      # else:
      #   shutil.rmtree(new_folder_path_2)
      #   break
    os.chdir(destination)


def run_code_sample(filepath_list, destination, i, t):
  # create virtual number of files
    images_jump = 1
    print(filepath_list[i])
    txt_name_log = open(destination + "/name_log.txt", "a")
    txt_name_log.write("{}, {}\n".format(("%03d" %(t)+"-" +"%03d"  %(i)), filepath_list[i]))
    txt_name_log.close()

    img = AICSImage(filepath_list[i])
    z_dim = img.shape[2]

    #dim for later for generating the image_3d files
    x_dim = img.shape[-2]
    y_dim = img.shape[-1]

    for j in range(z_dim-1):
      #create new directory-path
      file_folder = ("%03d" %(t)+"-" +"%03d"  %(i) + "-"+"%03d" %(j))

      os.chdir(destination)
      os.mkdir(file_folder)
      new_folder_path_2 = os.path.join(destination, file_folder)
      os.chdir(new_folder_path_2)

      #here put the image pngs into the folder (instead of creating the folder)
      #convert image to unit8 otherwise warning
      first = j* images_jump
      second = j*images_jump+images_jump
      if second <= z_dim-1: #*images_jump-images_jump:
        img_1 = img.get_image_data("YX", S=0, T=0, Z=0, C=first)
        img_1 = create_3D_image(img_1, x_dim, y_dim)
        img_1 = convert(img_1, 0, 255, np.uint8)

        img_2 = img.get_image_data("YX", S=0, T=0, Z=0, C=second)
        img_2 = create_3D_image(img_2, x_dim, y_dim)
        img_2 = convert(img_2, 0, 255, np.uint8)


        # saving images as PNG
        with png_writer.PngWriter("im1.png") as writer1:
          writer1.save(img_1)
        with png_writer.PngWriter("im3.png") as writer2:
          writer2.save(img_2)

    os.chdir(destination)
