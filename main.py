import cv2 as cv
import time
import pyttsx3
import logging
from config import (START, SMILE_SCREEN, FACE_RECOGNITION, FINAL_DISPLAY, 
                   ROI_X, ROI_Y, ROI_WIDTH, ROI_HEIGHT, 
                   START_IMAGE, SMILE_IMAGE, NEW_BG)
from sheets_manager import init_google_sheets, check_duplicate_name, append_to_google_sheets
from vision import detect_face_and_smile
from ui_manager import init_ui, draw_start_button, open_name_dialog, show_final_display

# Initialize global state variables as lists for mutability
current_state = [START]
smile_detected = [False]
participant_name = [""]
captured_frame = [None]
player_token = [""]
name_dialog_opened = [False]
smile_start_time = [None]
final_display_start_time = [None]
show_restart_button = [False]

# Initialize components
sheets_service = init_google_sheets()
try:
    engine = pyttsx3.init()
    logging.info("Text-to-speech engine initialized")
except Exception as e:
    logging.error(f"Failed to initialize text-to-speech: {e}")
    exit()

root = init_ui()
cap = cv.VideoCapture(0)
if not cap.isOpened():
    logging.error("Could not open webcam")
    exit()
cap.set(cv.CAP_PROP_FRAME_WIDTH, ROI_WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, ROI_HEIGHT)
logging.info("Webcam initialized")

def reset_to_start():
    current_state[0] = START
    smile_detected[0] = False
    participant_name[0] = ""
    captured_frame[0] = None
    player_token[0] = ""
    name_dialog_opened[0] = False
    smile_start_time[0] = None
    final_display_start_time[0] = None
    show_restart_button[0] = False
    logging.info("Reset to START state")

def mouse_callback(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        if current_state[0] == START:
            start_button_coords = param['start_button_coords']
            x1, y1, x2, y2 = start_button_coords
            if x1 <= x <= x2 and y1 <= y <= y2:
                current_state[0] = SMILE_SCREEN
                smile_start_time[0] = time.time()
                logging.info("Start button clicked - Transition to SMILE_SCREEN")
        elif current_state[0] == FINAL_DISPLAY and show_restart_button[0]:
            button_text = "RESTART"
            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 2
            (text_width, text_height), _ = cv.getTextSize(button_text, font, font_scale, thickness)
            button_x = (1920 - text_width) // 2
            button_y = (1080 - text_height)
            padding = 20
            if (button_x - padding <= x <= button_x + text_width + padding and 
                button_y - padding - text_height <= y <= button_y + padding):
                reset_to_start()

# Main loop
logging.info("Starting main loop")
while True:
    try:
        root.update()
        
        if current_state[0] == START:
            start_display, start_button_coords = draw_start_button(START_IMAGE.copy())
            cv.imshow('Monitoring', start_display)
            cv.setMouseCallback('Monitoring', mouse_callback, {'start_button_coords': start_button_coords})
        
        elif current_state[0] == SMILE_SCREEN:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to read frame from webcam")
                cv.imshow('Monitoring', SMILE_IMAGE)
                continue
            
            cv.imshow('Monitoring', SMILE_IMAGE)
            frame = cv.flip(frame, 1)
            frame, smile_detected[0] = detect_face_and_smile(frame, captured_frame)
            
            if smile_start_time[0] is not None and time.time() - smile_start_time[0] > 3:
                engine.say("Please smile!")
                engine.runAndWait()
                smile_start_time[0] = time.time()
                logging.debug("Voice prompt triggered")
            
            if smile_detected[0]:
                logging.info("Smile detected - Attempting transition to FACE_RECOGNITION")
                current_state[0] = FACE_RECOGNITION
                smile_detected[0] = False
                name_dialog_opened[0] = False
                logging.info("Transitioned to FACE_RECOGNITION")
        
        elif current_state[0] == FACE_RECOGNITION:
            bg_image = NEW_BG.copy()
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to read frame from webcam")
                continue
            
            frame = cv.flip(frame, 1)
            frame_with_shapes, _ = detect_face_and_smile(frame, captured_frame)
            frame_resized = cv.resize(frame_with_shapes, (ROI_WIDTH, ROI_HEIGHT))
            bg_image[ROI_Y:ROI_Y+ROI_HEIGHT, ROI_X:ROI_X+ROI_WIDTH] = frame_resized
            
            if participant_name[0]:
                text = f"Player: {participant_name[0]}"
                (tw, th), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 1.2, 2)
                text_x = ROI_X + (ROI_WIDTH - tw) // 2
                text_y = ROI_Y + ROI_HEIGHT + 50
                cv.putText(bg_image, text, (text_x, text_y),
                          cv.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            cv.imshow('Monitoring', bg_image)
            
            # Open dialog with local error handling
            if not name_dialog_opened[0] and not participant_name[0]:
                logging.debug("Calling open_name_dialog")
                try:
                    open_name_dialog(root, captured_frame, participant_name, player_token, name_dialog_opened,
                                    current_state, smile_start_time,
                                    lambda n: check_duplicate_name(sheets_service, n),
                                    lambda n, t: append_to_google_sheets(sheets_service, n, t))
                except Exception as dialog_error:
                    logging.error(f"Error in open_name_dialog: {str(dialog_error)}", exc_info=True)
                    current_state[0] = SMILE_SCREEN  # Revert to SMILE_SCREEN on error
                    smile_start_time[0] = time.time()
                    name_dialog_opened[0] = False
                logging.debug("open_name_dialog completed")
            
            if participant_name[0] and player_token[0]:
                logging.info("Name and token set - Transitioning to FINAL_DISPLAY")
                current_state[0] = FINAL_DISPLAY
                final_display_start_time[0] = time.time()
        
        elif current_state[0] == FINAL_DISPLAY:
            if final_display_start_time[0] and time.time() - final_display_start_time[0] > 5:
                show_restart_button[0] = True
            
            display_frame = show_final_display(captured_frame, participant_name[0], player_token[0], show_restart_button[0])
            cv.imshow('Monitoring', display_frame)
            cv.setMouseCallback('Monitoring', mouse_callback, {})

        key = cv.waitKey(1)
        if key == ord('q'):
            logging.info("Quitting program")
            break

    except Exception as e:
        logging.error(f"Error in main loop at state {current_state[0]}: {str(e)}", exc_info=True)
        break

# Cleanup
cap.release()
cv.destroyAllWindows()
root.destroy()
logging.info("Program terminated")