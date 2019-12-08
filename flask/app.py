import io
import json
import requests
import matplotlib.pyplot as plt

from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request
import base64


app = Flask(__name__)

# TODO Update with our skin disease model
#imagenet_class_index = json.load(open('<PATH/TO/.json/FILE>/imagenet_class_index.json'))
#model = models.densenet121(pretrained=True)
#model.eval()


def transform_image(image_bytes):
    """
    TODO modify to segment out potential moles from a photo
    Takes in input image data in bytes and transforms for input
    into ML model.

    :param image_bytes: raw image in byte array
    :return: transformed image
    """

    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    """
    Predict class for image
    :param image_bytes: input image
    :return: prediction
    """
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':

        img_dict = json.loads(json.dumps(request.json))
        print(img_dict)
        r = requests.get(img_dict["imgUrl"])
        print(r.content)
        with open('mark.png', 'wb') as f:
            f.write(r.content)


        #file = request.files['file']
        #img_bytes = file.read()
        #imgdata = base64.b64decode(imgstring)
        #print("received")
        #class_id, class_name = get_prediction(image_bytes=img_bytes)
        #return jsonify({'class_id': class_id, 'class_name': class_name})
        return ()


if __name__ == '__main__':
    app.run()