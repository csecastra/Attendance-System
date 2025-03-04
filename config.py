import cv2 as cv
import logging
import os

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1y56bOATGzEmlZVMfir7WB2QHs32iyKh7fK5g4FuewJI'
RANGE_NAME = 'Sheet1!A:B'
CHECK_RANGE = 'Sheet1!A:A'
CREDENTIALS_FILE = 'asthra-participant-list-55acad99e49d.json'

# Configuration
ROI_X, ROI_Y = 645, 130
ROI_WIDTH, ROI_HEIGHT = 630, 530
FRAME_W, FRAME_H = 666, 887
FRAME_POS = (1920 - FRAME_W - 150, 100)

# State machine constants
START, SMILE_SCREEN, FACE_RECOGNITION, FINAL_DISPLAY = 0, 1, 2, 3

# Paths and initial resources
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
START_IMAGE = cv.imread(os.path.join(BASE_DIR, 'Background/Desktop Inital.png'))
SMILE_IMAGE = cv.imread(os.path.join(BASE_DIR, 'Background/Desktop input.png'))
FINAL_BG = cv.imread(os.path.join(BASE_DIR, 'Background/Desktop final.png'))
NEW_BG = cv.imread(os.path.join(BASE_DIR, 'Background/new.png'))

# Cascade classifiers
FACE_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
SMILE_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_smile.xml')

# Validate resources
if any(img is None for img in [START_IMAGE, SMILE_IMAGE, FINAL_BG, NEW_BG]):
    logging.error("One or more background images not found")
    exit()
if FACE_CASCADE.empty() or SMILE_CASCADE.empty():
    logging.error("Failed to load cascade classifiers")
    exit()