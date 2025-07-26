from modules.voice1 import get_voice_input, speak_text
from modules.scence_desc import scene_desc
from modules.sensory_search import sensory_search, handle_follow_up_queries
from modules.sos import send_sos
from modules.iot import set_servo_angle
from modules.emotion import detect_emotion
from modules.ocr import ocr_text
from modules.face_add import *
from modules.face import *
def start():
    while True:
        set_servo_angle(90)
        print("Function is triggered")
        speak_text("Start to speak")
        
        while True:
            user_talk = get_voice_input()
            print(user_talk)  # Now returns text
            
            if user_talk:  # Ensure input is valid
                Scene_trigger = ["scene", "describe", "description", "seeing", "see"]
                sensory_trigger = ["sensory", "search", "holding", "buy"]
                sos_trigger = ["sos", "emergency", "help"]
                emotion_trigger = ["emotion", "feeling", "mood", "expression", "face", "reaction"]
                ocr_trigger = ["text", "ocr", "read", "extract", "recognize", "scan", "document"]
                face_add_trigger = ["add face", "register", "save face", "new person", "store face", "enroll","face enroll", "capture face", "remember", "add person", "insert face"]
                face_identify_trigger = ["identify", "who is this", "recognize", "detect face", "check face", "find person","who", "match face", "face check", "recognize person", "scan face", "face identity"]


                if any(word in user_talk for word in Scene_trigger):
                    set_servo_angle(90)
                    sc = scene_desc()
                    speak_text(sc)
                
                if any(word in user_talk for word in sensory_trigger):
                    a1 = sensory_search()
                    handle_follow_up_queries(a1)
                
                if any(word in user_talk for word in sos_trigger):
                    send_sos()
                
                if any(word in user_talk for word in ocr_trigger):
                    set_servo_angle(70)
                    ocr_text()

                if any(word in user_talk for word in emotion_trigger):
                    set_servo_angle(135)
                    detect_emotion()
                if any(word in user_talk for word in face_add_trigger):
                    set_servo_angle(135)
                    face_add()

                if any(word in user_talk for word in face_identify_trigger):
                    set_servo_angle(135)
                    facesd()

                if any(word in user_talk for word in ["exit", "stop", "bye"]):
                    speak_text("Exiting now.")
                    return             
            else:
                speak_text("No Input")

start()