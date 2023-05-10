PORT = 8080

CONF_CONTENT_THRESHOLD = 0.7
IOU_CONTENT_THRESHOLD = 0.7

CONF_CORNER_THRESHOLD = 0.8
IOU_CORNER_THRESHOLD = 0.5

CORNER_MODEL_PATH = "sources/Database/OCR/weights/corner.pt"
CONTENT_MODEL_PATH = "sources/Database/OCR/weights/content.pt"
OCR_MODEL_PATH = "sources/Database/OCR/weights/seq2seq.pth"

DEVICE = "cpu"  # or "cuda:0" if using GPU

# Config directory
UPLOAD_FOLDER = 'sources/Database/uploads'
SAVE_DIR = 'sources/static/results'

# Amazon Rekognition Config
COLLECTION_ID = "FaceDBSmartLock"
ACCESS_KEY_ID = "AKIAYJAR3NBVW27IY46R"
SECRET_ACCESS_ID = "BVf+fI9H3K0ReCkS+ZLOafk2uKZO+g6nwltDATM0"
