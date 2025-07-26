import google.generativeai as genai
import os
import cv2
import playsound
import tempfile
from modules.iot import get_frame
from modules.voice1 import * 
from PIL import Image
import time

# Assigning the API key
genai.configure(api_key="AIzaSyDRh_LmTo7-uGxYFbFDj0YRgESsoweYtJQ")

# Initialize the context
context = ""

def sensory_search():
    """
    Captures the scene description from the live feed using Google's Generative AI.
    """
    try:
        # Fetch a frame from the live feed using the get_frame() function
        frame = get_frame()
        
        if frame is None:
            print("Error: Could not fetch frame from live feed.")
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame_placeholder.image(frame, channels="RGB", use_container_width=True)
        # Save the captured frame temporarily as an image
        temp_image_path = tempfile.mktemp(suffix=".jpg")
        cv2.imwrite(temp_image_path, frame)
        # Load the captured image into PIL
        pic = Image.open(temp_image_path)
        
        # Prompt for scene description
        prompt = "Tell me about the object I am holding. What is this? and tell where can I buy this suggest both online and offline solutions.Describe as much as possible within 3 lines.Also do not use symbols like eg:(#,* etc)"
        
        # Use the generative model to generate the description
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([pic, prompt])
        
        # Output and return the response
        context=response.text
        print(context)
        speak_text(context)  # Scene description in text
        return context
    except Exception as e:
        print(f"An error occurred while generating scene description: {e}")
        return None

# Function to answer follow-up questions based on the context
def generate_response_with_context(user_input,context):
    if context:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            combined_input = context + "\n" + "User: " + user_input
            response = model.generate_content([combined_input])
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error generating response with context: {e}")
            return "Sorry, I couldn't process your request."
    else:
        return "There is no context available to respond to your question."

# Handling follow-up queries
def handle_follow_up_queries(context):
    while True:
        speak_text("You can ask follow-up questions or say 'exit' to end.")
        user_query = get_voice_input()

        if user_query:
            user_query = user_query.lower()
            if "exit" in user_query:
                speak_text("Exiting follow-up session.")
                print("Exiting follow-up session.")
                break
            else:
                print("Answering based on previous context...")
                response = generate_response_with_context(user_query,context)
                speak_text(response)
        else:
            speak_text("No valid input detected. Please try again or say 'exit' to end.")
            print("Invalid input for follow-up. Waiting for valid input...")
