from camera_handler import CameraHandler
from audio_handler import AudioHandler


class Streamer:
    def __init__(self):
        self.client = None
        self.camera_handler = CameraHandler()
        self.audio_handler = AudioHandler()
        self.initialized = False
    
    def initialize(self):
        if self.client is None:
            print("Error: No client. please set a client first")
        
        self.initialized = True
        print("Streamer initialized.")
    
    def set_client(self, client):
        if self.initialized:
            self.cleanup()
        self.client = client
    
    def start_stream(self):
        if not self.initialized:
            print("Error: Streamer not initialized. call initialize() method first")
            return
        
        try:
            streaming = True
            while streaming:
                video_chunk = self.get_video_chunk()
                audio_chunk = self.get_audio_chunk()

                if video_chunk is None or audio_chunk is None:
                    print("Error: Video or audio chunk is None. Skipping this iteration.")
                    continue

                try:
                    self.client.send_video(video_chunk)
                    self.client.send_audio(audio_chunk)
                except BrokenPipeError:
                    print("Error: Broken pipe. Reconnecting...")
                    self.client.reconnect()
        
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
            self.client.disconnect()
            self.initialized = False
