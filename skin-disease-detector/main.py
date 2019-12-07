import os
from glob import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils import data
from torchvision import models
from torchvision.transforms import Compose, RandomHorizontalFlip, RandomVerticalFlip, CenterCrop, RandomCrop, ToTensor, \
    Normalize

from data.dataset import SkiDiseaseDataset


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
    train_df, test_df = train_test_split(tile_df, test_size=0.1)
    validation_df, test_df = train_test_split(test_df, test_size=0.5)
    train_df = train_df.reset_index()
    validation_df = validation_df.reset_index()
    test_df = test_df.reset_index()
    composed = Compose([RandomHorizontalFlip(), RandomVerticalFlip(), CenterCrop(256), RandomCrop(224), ToTensor(),
                        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    # Define the trainingsset using the table train_df and using our defined transitions (composed)
    training_set = SkiDiseaseDataset(train_df, transform=composed)
    training_generator = data.DataLoader(training_set)
    # Same for the validation set:
    validation_set = SkiDiseaseDataset(validation_df, transform=composed)
    validation_generator = data.DataLoader(validation_set)
    resnext = models.resnext101_32x8d(pretrained=True)
    num_ftrs = resnext.fc.in_features
    resnext.fc = torch.nn.Linear(num_ftrs, 7)
    optimizer = torch.optim.Adam(resnext.parameters(), lr=1e-6)
    criterion = torch.nn.CrossEntropyLoss()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    max_epochs = 20
    trainings_error = []
    validation_error = []
    for epoch in range(max_epochs):
        print('epoch:', epoch)
        count_train = 0
        trainings_error_tmp = []
        resnext.train()
        for data_sample, y in training_generator:
            data_gpu = data_sample.to(device)
            y_gpu = y.to(device)
            output = resnext(data_gpu)
            err = criterion(output, y_gpu)
            err.backward()
            optimizer.step()
            trainings_error_tmp.append(err.item())
            count_train += 1
            if count_train >= 100:
                count_train = 0
                mean_trainings_error = np.mean(trainings_error_tmp)
                trainings_error.append(mean_trainings_error)
                print('trainings error:', mean_trainings_error)
                break
        with torch.set_grad_enabled(False):
            validation_error_tmp = []
            count_val = 0
            resnext.eval()
            for data_sample, y in validation_generator:
                data_gpu = data_sample.to(device)
                y_gpu = y.to(device)
                output = resnext(data_gpu)
                err = criterion(output, y_gpu)
                validation_error_tmp.append(err.item())
                count_val += 1
                if count_val >= 10:
                    count_val = 0
                    mean_val_error = np.mean(validation_error_tmp)
                    validation_error.append(mean_val_error)
                    print('validation error:', mean_val_error)
                    break
    plt.plot(trainings_error, label='training error')
    plt.plot(validation_error, label='validation error')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()



