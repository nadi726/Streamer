from abc import ABC, abstractmethod


class StreamClient(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def send_video(self, video_chunk):
        pass
    
    @abstractmethod
    def send_audio(self, audio_chunk):
        pass