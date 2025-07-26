import pyaudio
import wave
import pyttsx3
import warnings
from google.cloud import speech_v1 as speech
import os
import wave
import pyaudio
warnings.simplefilter("ignore", category=FutureWarning)


# Path to Google Cloud service account key
GCP_KEY_PATH = r"modules\elated-yen-446113-a9-1d192870cbf4.json"

# Initialize Google Speech-to-Text client
client = speech.SpeechClient.from_service_account_file(GCP_KEY_PATH)

def record_audio(output_file, duration=5, sample_rate=16000):
    """
    Records audio from the microphone and saves it as a WAV file.
    """
    chunk = 1024  # Buffer size
    format = pyaudio.paInt16  # 16-bit format
    channels = 1  # Mono
    rate = sample_rate  # Sample rate

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    
    print("Recording english speech... Speak now!")
    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def transcribe_audio(input_file):
    """
    Transcribe Tamil speech from the recorded audio file using Google Cloud Speech-to-Text.
    """
    with open(input_file, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            # language_code='ta-IN'
            language_code='en-US'
              # Tamil language code
        )
        
        response = client.recognize(config=config, audio=audio)
        
        for result in response.results:
            a=result.alternatives[0].transcript
        
        return a
def get_voice_input():
    recorded_audio = "recorded_tamil.wav"
    record_audio(recorded_audio, duration=5)  # Record for 5 seconds
    a=transcribe_audio(recorded_audio)
    return a



def speak_text(text):
    """Convert text to speech using pyttsx3."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
