import cv2 as cv
import tkinter as tk
from tkinter import messagebox
import os
import logging
import time  # Added for smile_start_time reset
from config import ROI_X, ROI_Y, ROI_WIDTH, ROI_HEIGHT, FRAME_W, FRAME_H, FRAME_POS, START_IMAGE, SMILE_IMAGE, FINAL_BG, NEW_BG, SMILE_SCREEN
from utils import generate_token

def init_ui():
    root = tk.Tk()
    root.withdraw()
    logging.info("Tkinter initialized")
    
    cv.namedWindow('Monitoring', cv.WINDOW_NORMAL)
    cv.setWindowProperty('Monitoring', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    cv.setWindowProperty('Monitoring', cv.WND_PROP_TOPMOST, 1)
    logging.info("OpenCV window configured")
    return root

def draw_start_button(image):
    button_text = "START"
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 2
    (text_width, text_height), _ = cv.getTextSize(button_text, font, font_scale, thickness)
    button_x = (1920 - text_width) // 2
    button_y = (1080 - text_height)
    padding = 20
    
    cv.rectangle(image, 
                 (button_x - padding, button_y - padding - text_height),
                 (button_x + text_width + padding, button_y + padding),
                 (0, 255, 0), -1)
    cv.putText(image, button_text, 
               (button_x, button_y), 
               font, font_scale, (255, 255, 255), thickness)
    return image, (button_x - padding, button_y - padding - text_height, 
                   button_x + text_width + padding, button_y + padding)

def open_name_dialog(root, captured_frame_ref, participant_name_ref, player_token_ref, name_dialog_opened_ref, current_state_ref, smile_start_time_ref, check_duplicate, append_to_sheets):
    if name_dialog_opened_ref[0]:
        return
    
    name_window = tk.Toplevel(root)
    name_window.title("Player Registration")
    dialog_width, dialog_height = 400, 150
    x_pos = ROI_WIDTH - 80
    y_pos = ROI_Y + ROI_HEIGHT - 70
    name_window.geometry(f"{dialog_width}x{dialog_height}+{x_pos}+{y_pos}")
    name_window.resizable(False, False)
    name_window.configure(bg='#2c3e50')
    name_window.attributes('-topmost', True)

    tk.Label(name_window, text="ENTER PLAYER NAME:", 
            font=('Arial', 14, 'bold'), bg='#2c3e50', fg='#ecf0f1').pack(pady=10)
    name_entry = tk.Entry(name_window, font=('Arial', 14), width=22)
    name_entry.pack(pady=5)
    
    def save_name():
        temp_name = name_entry.get().strip()
        if not temp_name:
            messagebox.showwarning("Input Error", "Please enter a name!", parent=name_window)
            return
        
        if check_duplicate(temp_name):
            messagebox.showinfo("Registration Error", "You are already registered!", parent=name_window)
            # Reset state to SMILE_SCREEN for re-detection
            current_state_ref[0] = SMILE_SCREEN
            participant_name_ref[0] = ""
            player_token_ref[0] = ""
            smile_start_time_ref[0] = time.time()
            name_dialog_opened_ref[0] = False
            name_window.destroy()
            logging.info("Duplicate name detected - Returning to SMILE_SCREEN")
            return
        
        participant_name_ref[0] = temp_name
        player_token_ref[0] = generate_token()
        picture_path = f"captures/{player_token_ref[0]}.png"
        
        if captured_frame_ref[0] is not None:
            if not os.path.exists("captures"):
                os.makedirs("captures")
            cv.imwrite(picture_path, captured_frame_ref[0])
            logging.info(f"Saved image: {picture_path}")
        
        append_to_sheets(participant_name_ref[0], player_token_ref[0])
        name_dialog_opened_ref[0] = False
        name_window.destroy()  # Close dialog after successful entry
    
    tk.Button(name_window, text="START GAME", command=save_name,
             bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
             width=12).pack(pady=5)
    
    name_dialog_opened_ref[0] = True
    name_window.focus_force()

def show_final_display(captured_frame_ref, participant_name, player_token, show_restart_button):
    display_frame = FINAL_BG.copy()
    
    if captured_frame_ref[0] is not None:
        resized_capture = cv.resize(captured_frame_ref[0], (FRAME_W, FRAME_H))
        display_frame[FRAME_POS[1]:FRAME_POS[1]+FRAME_H, 
                    FRAME_POS[0]:FRAME_POS[0]+FRAME_W] = resized_capture
        
        text_y = FRAME_POS[1] + 50
        cv.putText(display_frame, f"NAME: {participant_name.upper()}",
                  (FRAME_POS[0] + 50, text_y), 
                  cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv.putText(display_frame, f"TOKEN: {player_token}",
                  (FRAME_POS[0] + 50, text_y + 100), 
                  cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    if show_restart_button:
        button_text = "RESTART"
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 2
        (text_width, text_height), _ = cv.getTextSize(button_text, font, font_scale, thickness)
        button_x = (1920 - text_width) // 2
        button_y = (1080 - text_height)
        padding = 20
        cv.rectangle(display_frame, 
                    (button_x - padding, button_y - padding - text_height),
                    (button_x + text_width + padding, button_y + padding),
                    (0, 255, 0), -1)
        cv.putText(display_frame, button_text, 
                  (button_x, button_y), 
                  font, font_scale, (255, 255, 255), thickness)
    
    return display_frame