import os
import cv2
import time
import face_recognition
from statistics import mode, StatisticsError
from datetime import datetime
from modules.iot import get_frame
from modules.voice1 import speak_test

def load_known_faces():
    #change path where knownface is stores
    known_faces_dir = r".\known image"
    known_encodings = []
    known_names = []
    for filename in os.listdir(known_faces_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

def recognize_faces(image_path, known_encodings, known_names):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    recognized_faces = []
    for encoding in encodings:
        results = face_recognition.compare_faces(known_encodings, encoding)
        distances = face_recognition.face_distance(known_encodings, encoding)
        if any(results):
            best_match_index = distances.argmin()
            recognized_faces.append(known_names[best_match_index])
        else:
            recognized_faces.append("Unknown")
    return recognized_faces
def get_most_frequent_face_name(known_encodings, known_names, num_frames=3):
    recognized_list = []

    print("Capturing frames from ESP32-CAM and recognizing faces...")
    for i in range(num_frames):
        frame = get_frame()
        if frame is None:
            print(f"Frame {i+1}: Error fetching frame from ESP32-CAM.")
            continue

        temp_path = f"temp_frame_{i}.jpg"
        cv2.imwrite(0, frame)
        faces = recognize_faces(temp_path, known_encodings, known_names)
        print(f"Frame {i+1}: Recognized - {faces}")
        recognized_list.extend(faces)
        time.sleep(1)

    if not recognized_list:
        return "No faces detected."

    try:
        most_common = mode(recognized_list)
        speak_test(most_common)
        return f"Most frequently recognized face: {most_common}"
    except StatisticsError:
        return "No unique most frequent face (tie or none recognized)."


def facesd():
    known_encodings, known_names = load_known_faces()
    if not known_encodings:
        print("No known faces loaded. Please add images to the 'known image' directory.")
        return

    result = get_most_frequent_face_name(known_encodings, known_names)
    print(result)
    return result