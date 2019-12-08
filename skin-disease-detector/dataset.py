import torch
from PIL import Image
from pandas import DataFrame
from torch.utils import data


class SkiDiseaseDataset(data.Dataset):
    def __init__(self, df: DataFrame, transform=None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        X = Image.open(self.df['path'][index])
        y = torch.tensor(int(self.df['cell_type_idx'][index]))

        if self.transform:
            X = self.transform(X)

        return X, y
