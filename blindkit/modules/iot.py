import cv2
import urllib.request
import numpy as np
import requests

# Replace with the ESP32-CAM's live feed URL

ESP32_IP = "http://192.168.204.171"

def get_frame():
    """
    Fetches a single frame from the ESP32-CAM live feed.
    """
    try:
        img_resp = urllib.request.urlopen(f"{ESP32_IP}/cam-hi.jpg")
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)  # Decode image
        return frame
    except Exception as e:
        print(f"Error fetching frame: {e}")
        return None

# def get_frame():
#     """
#     Fetches a single frame from the ESP32-CAM video stream using OpenCV.
#     """
#     try:
#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():
#             print("Error: Cannot open video stream.")
#             return None

#         ret, frame = cap.read()
#         cap.release()

#         if not ret:
#             print("Error: Failed to read frame from stream.")
#             return None

#         return frame

#     except Exception as e:
#         print(f"Exception while fetching frame: {e}")
#         return None

    
def set_servo_angle(angle):
    url = f"{ESP32_IP}/servo_angle?value={angle}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Servo moved to angle {angle}°")
        else:
            print(f"Failed to move servo to angle {angle}°. HTTP Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
