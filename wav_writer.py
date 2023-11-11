import wave
from audio_handler import AudioHandler
from events import AudioListener


class WavWriter(AudioListener):
    FILENAME = "stream_audio.wav"

    def __init__(self):
        waveFile = wave.open(self.FILENAME, "wb")
        waveFile.setnchannels(AudioHandler.CHANNELS)
        waveFile.setsampwidth(2)
        waveFile.setframerate(AudioHandler.RATE)
        self.file = waveFile

    def on_audio(self, data):
        self.file.writeframes(data)