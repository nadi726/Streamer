from stream_handler import StreamHandler
import io
import wave
import sounddevice as sd

class AudioHandler(StreamHandler):
    # Constants for audio settings
    FORMAT = 'int16'  # Audio format (16-bit PCM)
    CHANNELS = 1       # Number of audio channels (1 for mono, 2 for stereo)
    RATE = 44100       # Sampling rate (samples per second)
    CHUNK = 1024       # Number of frames per buffer

    def __init__(self):
        self.audio_stream = sd.InputStream(
            samplerate=self.RATE,
            channels=self.CHANNELS,
            dtype=self.FORMAT,
            blocksize=self.CHUNK
        )
        self.audio_stream.start()
    
    def get(self):
        attempts = 0
        while attempts <= 3:
            audio_chunk, overflowed = self.audio_stream.read(self.CHUNK)
            if overflowed:
                attempts += 1
                continue
            byte_io = io.BytesIO()
            with wave.open(byte_io, "wb") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(16000)
                f.writeframes(audio_chunk.tobytes())
            byte_io.seek(0)
            return byte_io.read()

    def quit(self):
        self.audio_stream.stop()
        self.audio_stream.close()