from camera_handler import CameraHandler
from audio_handler import AudioHandler


class Streamer:
    def __init__(self):
        self.key = False
        self.clients = []
        self.camera_handler = CameraHandler()
        self.audio_handler = AudioHandler()
        self.initialized = False
    
    def initialize(self):
        self.initialized = True
        print("Streamer initialized.")
    
    def add_client(self, client):
        self.clients.append(client)
    
    def start_stream(self):
        if not self.initialized:
            print("Error: Streamer not initialized. call initialize() method first")
            return
        
        try:
            streaming = True
            while streaming:
                video_chunk = self.get_video_chunk()
                audio_chunk = self.get_audio_chunk()

                if video_chunk is not None and audio_chunk is not None:
                    for client in self.clients:
                        try:
                            client.send_video(video_chunk)
                            client.send_audio(audio_chunk)
                        except BrokenPipeError:
                            # Handle broken pipe error (e.g., attempt to reconnect)
                            print("Error: Broken pipe. Reconnecting...")
                            client.connect()  # Implement a method to reconnect to the streaming server

                else:
                    print("Error: Video or audio chunk is None. Skipping this iteration.")
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
        
    def get_video_chunk(self):
        video_chunk = self.camera_handler.get()
        if video_chunk == b"":
            print("null")
            return None

        return video_chunk
    def get_audio_chunk(self):
        audio_chunk = self.audio_handler.get()
        if audio_chunk == b"":
            print("null")
            return None
        return audio_chunk

    def cleanup(self):
        if self.initialized:
            self.camera_handler.quit()
            self.audio_handler.quit()
            self.initialized = False
        