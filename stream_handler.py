from abc import ABC, abstractmethod


class StreamHandler(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def quit(self):
        pass