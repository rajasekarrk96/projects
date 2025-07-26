import cv2
import torch
from torchvision import transforms, models
from PIL import Image
import numpy as np
from collections import Counter
from ultralytics import YOLO
from modules.iot import get_frame
from modules.voice1 import speak_text
emotion_labels = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral"
}

def get_convnext(model_size='large', num_classes=7):
    if model_size == 'tiny':
        model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights)
    elif model_size == 'small':
        model = models.convnext_small(weights=models.ConvNeXt_Small_Weights)
    elif model_size == 'base':
        model = models.convnext_base(weights=models.ConvNeXt_Base_Weights)
    else:
        model = models.convnext_large(weights=models.ConvNeXt_Large_Weights)
    model.classifier[2] = torch.nn.Linear(model.classifier[2].in_features, num_classes)
    return model

# Load models once
face_detector = YOLO(r"modules\yolo_face_detection.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
emotion_model = get_convnext(model_size='large', num_classes=7).to(device)
emotion_model.load_state_dict(torch.load(r"modules\model_epoch_5.pth", map_location=device))
emotion_model.eval()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def detect_emotion():
    predictions = []
    frame_count = 0

    while frame_count < 15:
        frame=get_frame()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detector.predict(source=rgb_frame, save=False, conf=0.5)
        detections = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()

        for det, conf in zip(detections, confidences):
            if conf < 0.5:
                continue

            xmin, ymin, xmax, ymax = map(int, det)
            h, w, _ = frame.shape
            x1 = max(xmin, 0)
            y1 = max(ymin, 0)
            x2 = min(xmax, w - 1)
            y2 = min(ymax, h - 1)

            face_img = rgb_frame[y1:y2, x1:x2]
            if face_img.size == 0:
                continue

            face_pil = Image.fromarray(face_img)
            input_tensor = preprocess(face_pil).unsqueeze(0).to(device)

            with torch.no_grad():
                logits = emotion_model(input_tensor)
                pred = int(logits.argmax(dim=1).item())
                predictions.append(pred)
            break  # Only take one face per frame

        frame_count += 1

    if predictions:
        most_common = Counter(predictions).most_common(1)[0][0]
        speak_text(f"emotion of person is{emotion_labels[most_common]}")
        return emotion_labels[most_common]
    else:
        return "No face detected"