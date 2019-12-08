from typing import Optional

import torch
from torchvision import transforms, datasets, models
from face_similarity.training import train_model_face


def main(root: str, model_path: Optional[str] = None):

    data_transform = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.49021736, 0.4212893, 0.39216894], std=[0.49021736, 0.4212893, 0.39216894])
    ])

    celeb_dataset = datasets.ImageFolder(root=root, transform=data_transform)
    dataset_loader = torch.utils.data.DataLoader(celeb_dataset, batch_size=32, shuffle=True, num_workers=4)

    if model_path is None:
        model = get_resnext()
    else:
        model = load_model(model_path)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-6)
    criterion = torch.nn.CrossEntropyLoss()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f'Device: {device}')

    model = train_model_face(model, criterion, optimizer, dataset_loader, len(celeb_dataset), device, num_epochs=10)
    torch.save(model.state_dict(), model_path)


def get_resnext():
    resnext = models.resnext101_32x8d(pretrained=True)
    for param in resnext.parameters():
        param.requires_grad = False
    num_ftrs = resnext.fc.in_features
    resnext.fc = torch.nn.Linear(num_ftrs, 190)
    if torch.cuda.is_available():
        resnext.cuda()
    return resnext


def load_model(model_path):
    model = get_resnext()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


if __name__ == '__main__':
    main('data_celeb', 'model_face.pth')

