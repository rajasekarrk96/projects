from PIL import Image
import google.generativeai as genai
from modules.iot import get_frame
from modules.voice1 import speak_text
import tempfile
import cv2

# Already configured earlier
genai.configure(api_key="your_api_key")

def ocr_text():
    """
    Captures a frame and uses Google Generative AI to extract readable text,
    then reads it aloud.
    """
    try:
        frame = get_frame()
        if frame is None:
            print("Error: Could not fetch frame from live feed.")
            return None

        # Convert to RGB for PIL
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Save frame temporarily
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame)

        # Load image with PIL
        pic = Image.open(temp_image_path)

        # Prompt for text extraction
        prompt = "You are an OCR assistant. Extract all readable text from this image and return only the text. No description, no labels, no greetings."

        # Use Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([pic, prompt])

        extracted_text = response.text.strip()
        print("Extracted Text:", extracted_text)

        if extracted_text:
            speak_text(extracted_text)
        else:
            print("No text detected.")

        return extracted_text or "No text found."

    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None
