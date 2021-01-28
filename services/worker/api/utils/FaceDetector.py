import numpy as np
import natsort
from PIL import Image
import shutil
import torch
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torchvision import transforms
from pathlib import Path
import os
from facenet_pytorch import MTCNN
import logging
logger = logging.getLogger(__name__)


post_process = False
image_size = 160
#TODO: make batch_size larger but need to make sure all images are the same size
batch_size = 1

class CustomDataSet(Dataset):
    def __init__(self, main_dir, all_imgs_paths, transform=None):
        self.main_dir = main_dir
        self.img_paths = all_imgs_paths
        self.transform = transform
        self.total_imgs = natsort.natsorted(self.img_paths)

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        #TODO: handle case when image is invalid
        img_loc = Path(self.main_dir) / Path(self.img_paths[idx])
        image = Image.open(str(img_loc)).convert("RGB")
        if self.transform:
            tensor_image = self.transform(image)
        else:
            tensor_image = image
        return (tensor_image, str(self.img_paths[idx]))


def format_path_for_repeats(img_path,oldvalue, newvalue):
    '''Used to replace some values in string path of file(from right side),
    and to change extension type to png(non-compressible)'''
    x = img_path.rfind(oldvalue)
    if x == -1:
        raise Exception("did not find index")
    replace_from_right_side = img_path[:x] + newvalue + img_path[x+len(oldvalue):] 
    return change_extension(replace_from_right_side)
def collate_fn(x):
    return x[0]
def create_dataset(repo_path, image_paths, transform=None, num_workers=0, batch_size=batch_size):
    logger.info("create dataset")
    dataset = CustomDataSet(main_dir=repo_path, all_imgs_paths=image_paths, transform=transform)
    loader = DataLoader(dataset, num_workers=num_workers,collate_fn=collate_fn,batch_size=batch_size)
    return dataset, loader
def change_extension(old):
    return os.path.splitext(old)[0]+'.png'
def get_face_path(path, repo_path, output_dir):
    logger.info("get_face_path")
    #since a file might be in some directory structure replace / with _
    save_to_path = str(Path(repo_path) / output_dir / path.replace('/','_'))
    counter  = 0
    save_to_path = format_path_for_repeats(save_to_path, ".", f"_{counter}.")
    path_exists = Path(save_to_path).exists()
    while path_exists:
        save_to_path = format_path_for_repeats(save_to_path, f"_{counter}.", f"_{counter+1}.")
        path_exists = Path(save_to_path).exists()
        counter+=1
    logger.info(f"save_to_path final is: {save_to_path}")
    return save_to_path

def detect_faces(mtcnn,dataset,loader, repo_path, output_dir):
    logger.info("detect_faces")
    img_paths = []
    face_paths = []
    faces = []
    for ii, _ in enumerate(loader):
        img, path = _
        try:
            with torch.no_grad():
                found_faces, prob = mtcnn(img, return_prob=True)
            if found_faces is not None:
                faces.extend(found_faces)
                num_faces = found_faces.shape[0] if found_faces.ndim == 4 else 1
                img_paths.extend([path]*num_faces)
                # write to file and store the file path
                for a_face in found_faces:
                    obj = np.moveaxis(a_face.cpu().numpy().astype(np.uint8),0,2)
                    im = Image.fromarray(obj)
                    new_path = get_face_path(path, repo_path, output_dir)
                    im.save(new_path)
                    without_repo = str(Path(str(new_path).replace(repo_path, "")))
                    face_paths.append(without_repo)
#                 print(f'Face {num_faces} facesdetected with probability {np.round(prob, 8)}')
                if ii % 10 == 0:
                    print(ii)
        except Exception as e:
            print(e)
    return (faces, img_paths, face_paths)


def create_faces(mtcnn, image_paths, repo_path, output_dir=".faces"):
    logger.info("create_faces")
    logger.info(f"image paths is: {image_paths}")
    logger.info(f"repo path is: {repo_path}")
    logger.info(f"output_dir is {output_dir}")
    mtcnn.eval()
    (Path(repo_path) / output_dir).mkdir(parents=True, exist_ok=True)
    # device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    train_dataset, train_loader = create_dataset(repo_path, image_paths)
    faces, faces_img_path, face_paths = detect_faces(mtcnn,train_dataset,train_loader, repo_path, output_dir)
    return list(zip(faces_img_path, face_paths))

if __name__ == "__main__":
    # repo_path="photos/seniors_hra/"
    output_dir="faces"


    image_paths = []
    extensions = ['.jpg','.JPG']
    for ext in extensions:
        for path in Path(repo_path).rglob(f"*{ext}"):
            if output_dir not in str(path):
                formatted_path = Path(str(path).replace(repo_path, ""))
                image_paths.append(str(formatted_path))
    print(image_paths)
                
    face_img_paths, face_paths, faces = create_faces(image_paths, repo_path, output_dir)
    assert len(face_img_paths) == len(face_paths)
    print(len(face_img_paths))

    # import pandas as pd
    # pd.DataFrame({'face_img_paths':face_img_paths,'face_paths':face_paths}).shape
    # assert (pd.DataFrame({'face_img_paths':face_img_paths,'face_paths':face_paths}) == pd.read_csv('test_against.csv',index_col=0)).all().all()
