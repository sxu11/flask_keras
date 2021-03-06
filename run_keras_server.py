
'''
Tutorial: https://blog.keras.io/building-a-simple-keras-deep-learning-rest-api.html
'''

from keras.applications.resnet50 import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
import tensorflow as tf
from PIL import Image

import numpy as np
import flask
import io

app = flask.Flask(__name__)
model = None

def load_model():
    global model
    global graph
    model = ResNet50(weights="imagenet")
    graph = tf.get_default_graph()

def prepare_image(image, target):
    if image.mode != 'RGB':
        image = image.convert("RGB")

    '''
    resize to 224*224 pixels
    '''
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)

    '''
    mean substraction and scaling
    '''
    image = imagenet_utils.preprocess_input(image)

    return image

@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dict that will be returned from the view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(224, 224))

            # classify the input image and then initialize the list
            # of predictions to return to the client
            with graph.as_default():
                preds = model.predict(image)
            results = imagenet_utils.decode_predictions(preds)
            data["predictions"] = []

            # loop over the results and add them to the list of
            # returned predictions
            for (imagenetID, label, prob) in results[0]:
                r = {"label":label, "probability":float(prob)}
                data["predictions"].append(r)

            # indicate that the request was a success
            data["success"] = True

        return flask.jsonify(data)

if __name__ == '__main__':
    print ("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started")
    load_model()
    app.run()