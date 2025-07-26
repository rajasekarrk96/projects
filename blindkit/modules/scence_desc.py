from PIL import Image
import google.generativeai as genai
from modules.iot import get_frame,set_servo_angle
import tempfile
import cv2
import time
# Configure the API key for Google Generative AI
genai.configure(api_key="your_api_key")  # Replace with your actual API key

def scene_desc():
    """
    Captures the scene description from the live feed using Google's Generative AI.
    """
    try:
        set_servo_angle(115)
        # Fetch a frame from the live feed using the get_frame() function
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from live feed.")
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame_placeholder.image(frame, channels="RGB", use_container_width=True)
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame)
        # Load the captured image into PIL
        pic = Image.open(temp_image_path)
        # Prompt for scene description
        prompt = "You are a describing assistant. Describe everything within 3 lines only return the descriptions no other things"
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([pic, prompt])
        
        # Output and return the response
        print(response.text) 
         # Scene description in text
        return response.text
    except Exception as e:
        print(f"An error occurred while generating scene description: {e}")
        return None