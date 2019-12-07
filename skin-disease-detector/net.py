import torch
import torchvision.models as models

resnext = models.resnext101_32x8d(pretrained=True)

num_ftrs = resnext.fc.in_features
resnext.fc = torch.nn.Linear(num_ftrs, 7)
