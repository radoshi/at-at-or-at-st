# Path: app.py
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from fastcore.all import *
from fastai.vision.all import *
from fastdownload import download_url

app = Flask(__name__)

db = DataBlock(
    blocks=(ImageBlock, CategoryBlock), 
    get_items=get_image_files, 
    splitter=RandomSplitter(valid_pct=0.2, seed=42),
    get_y=parent_label,
    item_tfms=[Resize(192, method='squish')]
)

uploads = Path(app.instance_path)/'uploads'
models = Path(app.instance_path)/'models'
models.mkdir(parents=True, exist_ok=True)

S3_URL = 'https://rushabh-ai-models.s3.us-west-2.amazonaws.com/trained.pth'
# download the model from S3
download_url(S3_URL, models)

data = Path('data')

dls = db.dataloaders(data, bs=32)
learn = vision_learner(dls, resnet18, metrics=error_rate)
learn.load('trained')

@app.route('/')
def hello_world():
    return render_template('index.html')

# create a post route for /check that gets a file as a post request
@app.route('/check', methods=['POST'])
def check():
    # get the file from the post request
    file = request.files['file']

    dec_pred, pred, probs = learn.predict(PILImage.create(file.stream))
    print(f'{dec_pred}, {pred}, {probs}')    

    # save the file to the uploads folder
    # if not uploads.exists():
    #     os.makedirs(uploads)
    
    # filename = uploads/secure_filename(file.filename)
    # file.save(filename)

    # print(f'File saved to {filename}')
    prediction = dec_pred.upper()
    probability = f'{(100 * probs[pred].item()):.02f}%'
    return render_template('result.html', prediction=prediction, probability=probability)
