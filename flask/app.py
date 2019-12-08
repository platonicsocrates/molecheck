import io
import json

import requests
import torch
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request

from flask.model_loading import load_model
from flask.class_to_celeb import class_to_celeb

app = Flask(__name__)

# TODO Update with our skin disease model
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = load_model('model_face.pth', device)


def transform_image(image_bytes):
    """
    TODO modify to segment out potential moles from a photo
    Takes in input image data in bytes and transforms for input
    into ML model.

    :param image_bytes: raw image in byte array
    :return: transformed image
    """

    transformations = transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.49021736, 0.4212893, 0.39216894], std=[0.49021736, 0.4212893, 0.39216894])
    ])

    image = Image.open(io.BytesIO(image_bytes))
    return transformations(image).unsqueeze(0)


def get_prediction(image_bytes) -> str:
    """
    Predict class for image
    :param image_bytes: input image
    :return: prediction
    """
    tensor = transform_image(image_bytes=image_bytes)
    tensor = tensor.to(device)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = y_hat.item()
    return class_to_celeb(predicted_idx)


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        img_dict = json.loads(json.dumps(request.json))
        r = requests.get(img_dict["imgUrl"])
        img_bytes = r.content
        name = get_prediction(img_bytes)
        return jsonify({'lookalike': name})


if __name__ == '__main__':
    app.run()
