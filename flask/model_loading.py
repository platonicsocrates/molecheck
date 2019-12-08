import torch
from torchvision import models


def get_resnext() -> models.resnext101_32x8d:
    resnext = models.resnext101_32x8d(pretrained=True)
    for param in resnext.parameters():
        param.requires_grad = False
    num_ftrs = resnext.fc.in_features
    resnext.fc = torch.nn.Linear(num_ftrs, 190)
    if torch.cuda.is_available():
        resnext.cuda()
    return resnext


def load_model(model_path: str, device: str) -> models:
    model = get_resnext()
    model.load_state_dict(torch.load(model_path, map_location=torch.device(device)))
    model.eval()
    return model
