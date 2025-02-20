import cv2
import face_recognition
import numpy as np
import time
import sqlite3
import pandas as pd
import smtplib
from email.message import EmailMessage

# Initialize Camera and Load Known Faces
def load_known_faces():
    known_faces = []
    known_names = []
    # Load images and encode them
    return known_faces, known_names

# Face Recognition and Attendance Marking
def recognize_faces(known_faces, known_names):
    cap = cv2.VideoCapture(0)  # Open Camera
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert Frame and Detect Faces
        # Compare and Mark Attendance
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Store Attendance in SQLite Database
def store_attendance(name):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, time.time()))
    conn.commit()
    conn.close()

# Export Attendance to Excel
def export_to_excel():
    conn = sqlite3.connect('attendance.db')
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    df.to_excel("attendance.xlsx", index=False)
    conn.close()

# Send Attendance via Email
def send_email():
    email_sender = "your_email@gmail.com"
    email_receiver = "faculty_email@gmail.com"
    subject = "Attendance Report"
    
    msg = EmailMessage()
    msg["From"] = email_sender
    msg["To"] = email_receiver
    msg["Subject"] = subject
    msg.set_content("Attached is the attendance report.")
    
    with open("attendance.xlsx", "rb") as file:
        msg.add_attachment(file.read(), maintype="application", subtype="xlsx", filename="attendance.xlsx")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_sender, "your_password")
        server.send_message(msg)

# Main Execution
if __name__ == "__main__":
    known_faces, known_names = load_known_faces()
    recognize_faces(known_faces, known_names)
    export_to_excel()
    send_email()
