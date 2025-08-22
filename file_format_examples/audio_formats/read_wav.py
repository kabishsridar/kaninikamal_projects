import wave
import numpy as np

with wave.open("apple_description.wav", "rb") as wav:
    print("Channels:", wav.getnchannels())
    print("Frame rate:", wav.getframerate())
    print("Frames:", wav.getnframes())
    frames = wav.readframes(1050)
    print("Raw bytes:", frames)

# ffmpeg -i sample.mp3 sample.wav to convert mp3 to wav
