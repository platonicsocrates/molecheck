import os
from glob import glob

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils import data
from torchvision import models
from torchvision.transforms import Compose, RandomHorizontalFlip, RandomVerticalFlip, CenterCrop, RandomCrop, ToTensor, \
    Normalize

from dataset import SkiDiseaseDataset
from training import train_model


def main():
    base_skin_dir = os.path.join('.', 'data')
    imageid_path_dict = {os.path.splitext(os.path.basename(x))[0]: x
                         for x in glob(os.path.join(base_skin_dir, '*', '*.jpg'))}
    lesion_type_dict = {
        'nv': 'Melanocytic nevi',
        'mel': 'dermatofibroma',
        'bkl': 'Benign keratosis-like lesions ',
        'bcc': 'Basal cell carcinoma',
        'akiec': 'Actinic keratoses',
        'vasc': 'Vascular lesions',
        'df': 'Dermatofibroma'
    }
    tile_df = pd.read_csv(os.path.join(base_skin_dir, 'HAM10000_metadata.csv'))
    tile_df['path'] = tile_df['image_id'].map(imageid_path_dict.get)
    tile_df['cell_type'] = tile_df['dx'].map(lesion_type_dict.get)
    tile_df['cell_type_idx'] = pd.Categorical(tile_df['cell_type']).codes
    tile_df[['cell_type_idx', 'cell_type']].sort_values('cell_type_idx').drop_duplicates()
    train_df, validation_df = train_test_split(tile_df, test_size=0.2)
    train_df = train_df.reset_index()
    validation_df = validation_df.reset_index()
    composed = Compose([RandomHorizontalFlip(), RandomVerticalFlip(), CenterCrop(256), RandomCrop(224), ToTensor(),
                        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    # Define the trainingsset using the table train_df and using our defined transitions (composed)
    training_set = SkiDiseaseDataset(train_df, transform=composed)
    training_generator = data.DataLoader(training_set, batch_size=64, shuffle=True)
    # Same for the validation set:
    validation_set = SkiDiseaseDataset(validation_df, transform=composed)
    validation_generator = data.DataLoader(validation_set, batch_size=64, shuffle=True)

    dataloaders = dict(train=training_generator, val=validation_generator)
    dataset_size = dict(train=len(training_set), val=len(validation_set))

    model = get_resnext()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-6)
    criterion = torch.nn.CrossEntropyLoss()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f'Device: {device}')

    model = train_model(model, criterion, optimizer, dataloaders, dataset_size, device)
    torch.save(model.state_dict(), 'model.pth')


def get_resnext():
    resnext = models.resnext101_32x8d(pretrained=True)
    for param in resnext.parameters():
        param.requires_grad = False
    num_ftrs = resnext.fc.in_features
    resnext.fc = torch.nn.Linear(num_ftrs, 7)
    if torch.cuda.is_available():
        resnext.cuda()
    return resnext


def load_model():
    model = get_resnext()
    model.load_state_dict(torch.load('model.pth'))
    model.eval()
    return model


if __name__ == '__main__':
    main()
