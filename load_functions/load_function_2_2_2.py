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


def get_img_path_list_Z(img_path_list, filepath):
  ''' Creates a list of image-path that will be used for loading the images later'''
  flist = os.listdir(filepath)
  flist.sort()
  for i in flist:
    img_slice_path = os.path.join(filepath, i)
    img_path_list.append(img_slice_path)
  return img_path_list
# img_path_list = get_img_path_list_Z(img_path_list, filepath, folder_list)
# img_path_list

def load_img_Z(img_path, channel, t, divisor):
    img = AICSImage(img_path)
    img = img.get_image_data("ZYX", S=0, T=channel, C=t) ### because the image gets read in like that
    # img = img.get_image_data("YX", S=0, T=0, C=0, Z=0)
    # print(img.shape, img.dtype)
    x_dim = img.shape[1]
    y_dim = img.shape[2]
    x_div = x_dim//divisor
    y_div = y_dim//divisor
    return img, x_div, y_div


def create_foldersystem_Z(root, img_path_list, divisor, ticker):
  #### Create folder structure ####
  img = AICSImage(img_path_list[0])
  # img = img.get_image_data("ZYX", C=0 S=0, T=0,)
  print(img.shape)
  image_resolution = img.shape[-1]
  nr_z_slices = img.shape[3]
  nr_channels = img.shape[1]
  nr_timepoints = img.shape[2]
  x_dim = img.shape[-1]
  y_dim = img.shape[-2] 
  print("The Resolution is: " + str(image_resolution))
  print("The number of z-slizes is: " + str(nr_z_slices))
  print("The number of timepoints: " + str(nr_timepoints))
  print("The number of channels: " + str(nr_channels))

  multiplyer = image_resolution/divisor
  # z-dimension
  z = 0
  # k ist for different z-depth points/files
  k = 0

  channel_dict = {}
  os.chdir(root)
  destination = root

  # remove folder if there was one before
  # create new folder
  if ticker == "yes":
    if os.path.exists(destination):
      shutil.rmtree(destination)
      os.mkdir(destination)
      os.chdir(destination)
      for i in range(nr_channels):
        os.mkdir("%d" %(i))
        channel_dict[("{}".format(i))] = os.path.join(destination,("{}".format(i)))
    else:
      os.mkdir(destination)
      os.chdir(destination)
      for i in range(nr_channels):
        os.mkdir("%d" %(i))      # think how I can make a dictionary with the idfferent channels and destinations
        channel_dict[("{}".format(i))] = os.path.join(destination,("{}".format(i)))
  else:
    if os.path.exists(destination):
      for i in range(nr_channels):
        channel_dict[("{}".format(i))] = os.path.join(destination,("{}".format(i)))
    else:
      os.chdir(destination)
      for i in range(nr_channels):
        channel_dict[("{}".format(i))] = os.path.join(destination,("{}".format(i)))
  os.chdir(destination)

  # os.chdir(split_img_path)
  return nr_channels, nr_z_slices, nr_timepoints, destination, multiplyer, channel_dict
 
def run_code_Z(destination, img_path_list, nr_channels, nr_timepoints, nr_z_slices, multiplyer, channel_dict, divisor):
  #remove old log file if already existing
  # z-dimension
  # t = 0    ## for some reaosn I need to define the t outside of the function
  # k ist for different z-depth points/files
  # k = 0

  #remove old log file if already existing
  log_file_name = os.path.join(destination,"name_log.txt")
  if os.path.exists(log_file_name):
    os.remove(log_file_name)
  for k in tqdm(range(len(img_path_list))):
      for channel in range(nr_channels):
        for t in range(nr_timepoints):
          try:
            img, x_div, y_div = load_img_Z(img_path_list[k], channel, t, divisor)
            # print(image_resolution)
            # log the names together
            txt_name_log = open(log_file_name, "a")
            txt_name_log.write("{}, {}\n".format(("%03d" %(k)+"-" +"%03d"  %(t)), img_path_list[k]), )
            txt_name_log.close()
            for i in range(x_div):
              for j in range(y_div):
                img_crop = img
                # print(str((i*divisor))+":"+ str(((i+1)*divisor))+":" +","+ str((j*divisor))+":"+str(((j+1)*divisor))+":")
                img_crop = img_crop[:,(i*divisor):((i+1)*divisor):,(j*divisor):((j+1)*divisor)]
                # cv2_imshow(img_crop)
                name = ("%03d" %(k)+"-" +"%03d"  %(t) + "-"+"%02d" %((i*multiplyer)+j))
                #swap the axis to be able to save as tif file
                # img_crop = np.swapaxes(img_crop, 2, 0)
                print("saving image {}".format(name))
                os.chdir(channel_dict[str(channel)])
                with OmeTiffWriter("{}.tif".format(name)) as writer2:
                  writer2.save(img_crop)         
          except:
            print("This file has a smaller T-dimension that the first one loaded")

# run_code_Z(destination, img_path_list, nr_channels, nr_timepoints, nr_z_slices, multiplyer, channel_dict)
