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
            dtype=self.FORMAT,
            device=3  # Adjust this to the appropriate input device index
        )
        self.thread = threading.Thread(target=self.get_audio_thread)    

    def get_audio_thread(self):
        while True:
            data, overflowed = self.audio_stream.read(self.CHUNK)
            if not overflowed:
                EventEmitter.trigger_audio_event(data.tobytes())

    def start_thread(self):
        self.audio_stream.start()
        self.thread.start()
