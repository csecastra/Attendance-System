import cv2 as cv
import numpy as np
import random
import logging
from config import FACE_CASCADE, SMILE_CASCADE

def detect_face_and_smile(frame, captured_frame_ref):
    smile_detected = False
    try:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        frame_copy = frame.copy()
        if len(faces) > 0:
            x, y, w, h = faces[0]
            shape_type = random.choice(['square', 'triangle', 'circle'])
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
            if shape_type == 'square':
                cv.rectangle(frame_copy, (x, y), (x+w, y+h), color, 3)
            elif shape_type == 'triangle':
                pt1 = (x + w//2, y)
                pt2 = (x, y+h)
                pt3 = (x+w, y+h)
                cv.drawContours(frame_copy, [np.array([pt1, pt2, pt3])], 0, color, 3)
            elif shape_type == 'circle':
                cv.circle(frame_copy, (x+w//2, y+h//2), min(w,h)//2, color, 3)
            
            captured_frame_ref[0] = frame_copy[y:y+h, x:x+w]
            if len(SMILE_CASCADE.detectMultiScale(gray[y:y+h, x:x+w], 1.8, 20)) > 0:
                smile_detected = True
        return frame_copy, smile_detected
    except Exception as e:
        logging.error(f"Error in detect_face_and_smile: {e}")
        return frame, False