
def get_folder_list(filepath, folder_list):
  '''gets a list of folders as basis for the reconstruction'''
  for i in os.listdir(filepath):
    folder_list.append(i)
  folder_list.sort()
  return folder_list

def get_img_path_list(img_path_list, filepath, folder_list):
  ''' Creates a list of image-path that will be used for loading the images later'''
  for i in folder_list:
    path_images = os.path.join(filepath,i)
    os.chdir(path_images)
    flist = os.listdir(path_images)
    flist.sort()
    # flist = flist[:-1]  # to remove the last image of the series - will be the first one of the following one
    for j in flist:
      img_slice_path = os.path.join(path_images, j)
      img_path_list.append(img_slice_path)
  return img_path_list


def get_identifyer(img_path_single):
  '''isolates the file_identifyer number middle 3 numbers from the folder 
  which symbolise the frame z-stack number of the image'''
  splitter_1 = "/"
  folder = img_path_single.split(splitter_1)[-2]
  splitter_2 = "-"
  identifyer = folder.split(splitter_2)[-2]
  # print(identifyer)
  return identifyer

def get_folder_identifyer(img_path_single):
  splitter_1 = "/"
  folder = img_path_single.split(splitter_1)[-2]
  splitter_2 = "-"
  folder_identifyer = folder.split(splitter_2)[-1]
  # print(folder_identifyer)
  return folder_identifyer

def get_img_slice(img_path_single, dim):
  '''loads and transforms the image into the right format''' 
  img1 = AICSImage(img_path_single)
  img1 = img1.get_image_data("ZYX", C=0, S=0, T=0)  # returns 4D CZYX numpy array
  img_temp = np.zeros((1,1,dim,dim))
  img_temp[0] = img1
  return img_temp
  
def create_folders(root, folder_name):  
  os.chdir(root)
  destination = os.path.join(root,folder_name)
  # remove folder if there was one before
  # create new folder
  if os.path.exists(destination):
    shutil.rmtree(destination)
    os.mkdir(destination)
  else:
    os.mkdir(destination)
  os.chdir(destination)
  return destination
