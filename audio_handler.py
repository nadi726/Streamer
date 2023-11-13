import sounddevice as sd
import threading
import numpy as np
from events import EventEmitter

class AudioHandler:
    # Constants for audio settings
    FORMAT = np.int16          # Audio format (16-bit PCM)
    CHANNELS = 1               # Number of audio channels (1 for mono, 2 for stereo)
    RATE = 44100               # Sampling rate (samples per second)
    CHUNK = 1024               # Number of frames per buffer

    def __init__(self):
        self.audio_stream = sd.InputStream(
            channels=self.CHANNELS,
            samplerate=self.RATE,
            blocksize=self.CHUNK,
            callback=self.callback,
            dtype=self.FORMAT,
            device=3  # Adjust this to the appropriate input device index
        )
        self.thread = threading.Thread(target=self.get_audio_thread)
    
    def callback(self, indata, frames, time, status):
        if status:
            print(f"Error in callback: {status}")
        if frames > 0:
            data = indata.tobytes()
            EventEmitter.trigger_audio_event(data)

    def get_audio_thread(self):
        with self.audio_stream:
            sd.sleep(1000000)  # Use a long sleep to keep the stream open

    def start_thread(self):
        self.thread.start()
