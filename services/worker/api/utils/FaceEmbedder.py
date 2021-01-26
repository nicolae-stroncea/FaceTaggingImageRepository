from facenet_pytorch import InceptionResnetV1
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import numpy as np
import torch
import natsort
from PIL import Image
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
from torchvision.transforms import functional as F


# from: https://github.com/timesler/facenet-pytorch/blob/master/models/mtcnn.py
def fixed_image_standardization(image_tensor):
    processed_tensor = (image_tensor - 127.5) / 128.0
    return processed_tensor

class InceptionDataSet(Dataset):
    def __init__(self, main_dir, all_imgs_paths, transform=None, process=True):
        self.main_dir = main_dir
        self.img_paths = all_imgs_paths
        self.transform = transform
#         self.total_imgs = natsort.natsorted(self.img_paths)
        self.process = process

    def __len__(self):
        return len(self.img_paths)
    def __getitem__(self, idx):
        img_loc = Path(self.main_dir) / Path(self.img_paths[idx])
#         image = Image.open(str(img_loc)).convert("RGB")
#         tensor_image = F.to_tensor(np.float32(image))
        tensor_image = F.to_tensor(np.float32(Image.open(img_loc)))
        if self.process:
            tensor_image = fixed_image_standardization(tensor_image)
        return tensor_image, str(self.img_paths[idx])

def create_dataset_inception(repo_path, image_paths, batch_size, transform=None, num_workers=0):
    dataset = InceptionDataSet(main_dir=repo_path, all_imgs_paths=image_paths, transform=transform)
    loader = DataLoader(dataset, num_workers=num_workers,batch_size=batch_size, shuffle=False)
    return dataset, loader


def get_embeddings(repo_path, face_paths, batch_size):
    logger.info(f"starting to embed {len(face_paths)} faces")
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    dataset, loader = create_dataset_inception(repo_path, face_paths, batch_size)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    embeddings = []
    all_paths = []
    for imgs, paths in loader:
        logger.info("ran 1 batch")
        with torch.no_grad():
            embeddings.append(resnet(imgs))
            all_paths.extend(paths)
    embeddings = [el for el in torch.cat(embeddings)]
    # assert all embeddings are 512 in size
    assert len(all_paths) == len(face_paths)
    assert len(embeddings) == len(all_paths)
    assert sum([el.numel() == 512 for el in embeddings]) == len(embeddings)
    return embeddings, all_paths