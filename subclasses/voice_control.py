import pyaudio
import wave
import os
import openai
import threading
from termcolor import colored

# set up the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY"

# Initialize OpenAI client
client = openai.OpenAI()

# Constants for audio recording
CHUNK = 1024
SAMPLE_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100



def record_audio():
    global is_recording

    # Global variable to control the recording loop
    is_recording = True
    
    p = pyaudio.PyAudio()

    transcript = ""
    
    print("Press Enter to start recording...")
    input()
    
    print("Recording started. Press Enter again to stop recording...")
    stream = p.open(format=SAMPLE_FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    frames_per_buffer=CHUNK,
                    input=True)
    
    stream.start_stream()
    frames = []
    
    def recording_loop():
        while is_recording:
            data = stream.read(CHUNK)
            frames.append(data)
            if not is_recording:
                print("Recording stopped.")
                break

    recording_thread = threading.Thread(target=recording_loop)
    recording_thread.start()

    input()
    is_recording = False
    recording_thread.join()

    filename = 'output.wav'
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print("Transcribing audio file...")
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        print(transcript)

    os.remove(filename)


    stream.stop_stream()
    stream.close()
    p.terminate()
    with open('recording.txt', 'w') as f:
        f.write(transcript.text)

    return transcript.text