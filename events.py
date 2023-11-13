"""A basic implementation of an event system with two listener interfaces: FrameListener and AudioListener."""

from abc import ABC, abstractmethod

class FrameListener(ABC):
    @abstractmethod
    def on_frame(self, data):
        pass

class AudioListener(ABC):
    @abstractmethod
    def on_audio(self, data):
        pass


class EventEmitter:
    frame_listeners = []       
    audio_listeners = []

    @classmethod
    def add_frame_listener(cls, listener):
        cls.frame_listeners.append(listener)
    @classmethod
    def remove_frame_listener(cls, listener):
        cls.frame_listeners.remove(listener)
    @classmethod
    def trigger_frame_event(cls, data):
        for listener in cls.frame_listeners:
            listener.on_frame(data)
    @classmethod
    def add_audio_listener(cls, listener):
        cls.audio_listeners.append(listener)
    @classmethod
    def remove_audio_listener(cls, listener):
        cls.audio_listeners.remove(listener)
    @classmethod
    def trigger_audio_event(cls, data):
        for listener in cls.audio_listeners:
            listener.on_audio(data)