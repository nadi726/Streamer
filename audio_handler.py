from stream_handler import StreamHandler
import pyaudio

class AudioHandler(StreamHandler):
    # Constants for audio settings
    FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
    CHANNELS = 1               # Number of audio channels (1 for mono, 2 for stereo)
    RATE = 44100               # Sampling rate (samples per second)
    CHUNK = 1024               # Number of frames per buffer

    def __init__(self):
        self.audio_stream = pyaudio.PyAudio().open(format=self.FORMAT,
                                                    channels=self.CHANNELS,
                                                    rate=self.RATE,
                                                    input=True,
                                                    frames_per_buffer=self.CHUNK)
    
    def get(self):
        audio_chunk = self.audio_stream.read(self.CHUNK, exception_on_overflow = False)
        return audio_chunk

    def quit(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()