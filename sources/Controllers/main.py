import os

import databases
import numpy as np
import sources.Controllers.config as cfg
import yolov5
from PIL import Image
from fastapi import Request, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sources import app, templates
from sources.Controllers import utils, rekognition, database_management
from sources.Models import models
from sources.Models.database import engine, SQLALCHEMY_DATABASE_URL
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor

""" ---- Setup ---- """
# Init Database
database = databases.Database(SQLALCHEMY_DATABASE_URL)
models.Base.metadata.create_all(bind=engine)


# Startup database server before start app
@app.on_event("startup")
async def startup_database():
    await database.connect()


# Shutdown database sever after closed app
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Init yolov5 model
CORNER_MODEL = yolov5.load(cfg.CORNER_MODEL_PATH)
CONTENT_MODEL = yolov5.load(cfg.CONTENT_MODEL_PATH)

# Set conf and iou threshold -> Remove overlap and low confident bounding boxes
CONTENT_MODEL.conf = cfg.CONF_CONTENT_THRESHOLD
CONTENT_MODEL.iou = cfg.IOU_CONTENT_THRESHOLD

CORNER_MODEL.conf = cfg.CONF_CORNER_THRESHOLD
CORNER_MODEL.iou = cfg.IOU_CORNER_THRESHOLD

# Config directory
UPLOAD_FOLDER = cfg.UPLOAD_FOLDER
SAVE_DIR = cfg.SAVE_DIR

""" Recognizion detected parts in ID """
config = Cfg.load_config_from_name('vgg_seq2seq')  # OR vgg_transformer -> acc || vgg_seq2seq -> time
config['weights'] = cfg.OCR_MODEL_PATH
config['cnn']['pretrained'] = False
config['device'] = cfg.DEVICE
config['predictor']['beamsearch'] = False
detector = Predictor(config)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/extractor")
async def id_extract_page(request: Request):
    return templates.TemplateResponse("id-card-extractor.html", {"request": request})


@app.get("/ekyc")
async def ekyc_page(request: Request):
    return templates.TemplateResponse("ekyc.html", {"request": request})


@app.post("/uploader")
async def upload(file: UploadFile = File(...)):
    input_images_list = os.listdir(UPLOAD_FOLDER)
    if input_images_list is not None:
        for uploaded_img in input_images_list:
            os.remove(os.path.join(UPLOAD_FOLDER, uploaded_img))

    file_location = f"./{UPLOAD_FOLDER}/{file.filename}"
    contents = await file.read()
    with open(file_location, 'wb') as f:
        f.write(contents)

    # Validating file
    input_file = os.listdir(UPLOAD_FOLDER)[0]
    if input_file == 'NULL':
        os.remove(os.path.join(UPLOAD_FOLDER, input_file))
        error = "No file selected!"
        return JSONResponse(status_code=403, content={"message": error})
    elif input_file == 'WRONG_EXTS':
        os.remove(os.path.join(UPLOAD_FOLDER, input_file))
        error = "This file is not supported!"
        return JSONResponse(status_code=404, content={"message": error})

    return await extract_info()


@app.post("/extract")
async def extract_info(ekyc=False, path_id=None):
    """ Check if uploaded image exist """
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    input_images_list = os.listdir(UPLOAD_FOLDER)
    if input_images_list is not None:
        if not ekyc:
            img = os.path.join(UPLOAD_FOLDER, input_images_list[0])
        else:
            img = path_id

    corner_model = CORNER_MODEL(img)
    predictions = corner_model.pred[0]
    categories = predictions[:, 5].tolist()  # Class
    if len(categories) != 4:
        error = "Detecting corner failed!"
        return JSONResponse(status_code=401, content={"message": error})
    boxes = utils.class_order(predictions[:, :4].tolist(), categories)  # x1, x2, y1, y2

    image = Image.open(img)
    center_points = list(map(utils.get_center_point, boxes))

    """ TODO: Temporary fixing """
    c2, c3 = center_points[2], center_points[3]
    c2_fix, c3_fix = (c2[0], c2[1] + 30), (c3[0], c3[1] + 30)
    center_points = [center_points[0], center_points[1], c2_fix, c3_fix]
    center_points = np.asarray(center_points)
    aligned = utils.four_point_transform(image, center_points)
    # Convert from OpenCV to PIL format
    aligned = Image.fromarray(aligned)

    content_model = CONTENT_MODEL(aligned)
    predictions = content_model.pred[0]
    categories = predictions[:, 5].tolist()  # Class
    if 7 not in categories:
        if len(categories) < 9:
            error = "Missing fields! Detecting content failed!"
            return JSONResponse(status_code=402, content={"message": error})
    elif 7 in categories:
        if len(categories) < 10:
            error = "Missing fields! Detecting content failed!"
            return JSONResponse(status_code=402, content={"message": error})

    boxes = predictions[:, :4].tolist()

    """ Non Maximum Suppression """
    boxes, categories = utils.non_max_suppression_fast(np.array(boxes), categories, 0.7)
    boxes = utils.class_order(boxes, categories)  # x1, x2, y1, y2
    if not os.path.isdir(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    else:
        for f in os.listdir(SAVE_DIR):
            os.remove(os.path.join(SAVE_DIR, f))

    for index, box in enumerate(boxes):
        left, top, right, bottom = box
        if 5 < index < 9:
            right = right + 100
        cropped_image = aligned.crop((left, top, right, bottom))
        cropped_image.save(os.path.join(SAVE_DIR, f'{index}.jpg'))

    detected_fields = []  # Collecting all detected parts
    for idx, img_crop in enumerate(sorted(os.listdir(SAVE_DIR))):
        if idx > 0:
            img_ = Image.open(os.path.join(SAVE_DIR, img_crop))
            s = detector.predict(img_)
            detected_fields.append(s)

    if 7 in categories:
        detected_fields = detected_fields[:6] + [detected_fields[6] + ', ' + detected_fields[7]] + [detected_fields[8]]

    face_img_path = os.path.join(SAVE_DIR, f'0.jpg')

    if rekognition.check_existed_face(face_img_path) != None:
        print("EXISTED FACE!")
    else:
        face_id = rekognition.add_face_to_collection(face_img_path)
        database_management.add_record_to_db(detected_fields, face_id)

    response = {
        "data": detected_fields
    }

    response = jsonable_encoder(response)

    return JSONResponse(content=response)


@app.post("/download")
async def download(file: str = Form(...)):
    if file != 'undefined':
        noti = 'Download file successfully!'
        return JSONResponse(status_code=201, content={"message": noti})
    else:
        error = 'No file to download!'
        return JSONResponse(status_code=405, content={"message": error})
