import cv2
import os
import time
from modules.voice1 import get_voice_input,speak_test
from modules.iot import get_frame
# Dynamic Output Directory
OUTPUT_DIR = os.path.join(os.getcwd(), "known image")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Load Face Detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# def detect_faces(frame):
#     """ Detect faces in a given frame using OpenCV Haar Cascade. """
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(40, 40))
#     return faces

def detect_faces(frame):
    """ Detect faces in a given frame using OpenCV Haar Cascade. """
    frame_resized = cv2.resize(frame, (640, 480))  # Resize for consistent detection
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    gray = cv2.equalizeHist(gray)  # Improve contrast
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces


def face_add():
    """ Capture, detect faces, get a name, and save the image with the recognized name. """
    
    print("📷 Capturing image from webcam...")
    frame = get_frame()
    # Detect faces
    faces = detect_faces(frame)
    if len(faces) == 0:
        print("⚠️ No face detected! Try adjusting the camera angle or lighting.")
        return None

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # # Show the frame with detected faces
    # cv2.imshow("Face Detection", frame)
    # cv2.waitKey(2000)  # Display for 2 seconds
    # cv2.destroyAllWindows()

    # Get Name via Voice
    print("🎤 Please say your name...")
    speak_test("Please say name of the person")
    person_name = get_voice_input()
    
    # Fallback to Manual Input
    if not person_name:
        person_name = input("Couldn't detect name. Enter manually: ").strip()
        if not person_name:
            print("❌ No name provided! Image not saved.")
            return None

    # Generate Unique File Name
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_name = f"{person_name}_{timestamp}.jpg"
    output_path = os.path.join(OUTPUT_DIR, file_name)

    # Save the image
    cv2.imwrite(output_path, frame)
    print(f"✅ Image saved as: {output_path}")

    # Store name in a text file (for reference)
    with open(os.path.join(OUTPUT_DIR, "face_log.txt"), "a") as f:
        f.write(f"{person_name}, {output_path}\n")

    return person_name  # Return the detected name for further use
