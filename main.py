from abc import ABC, abstractmethod
import os
import io
import subprocess
import time
import socket
import cv2
import pyaudio


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


class LiveStream(StreamClient):
    YOUTUBE_ENDPOINT = "rtmp://a.rtmp.youtube.com/live2"
    
    def __init__(self, broadcast_key):
        self.stream_url = f"{self.YOUTUBE_ENDPOINT}/{broadcast_key}"
        self.connect()

    def connect(self):
        command = [
            "ffmpeg",
            "-re",
            "-i", "pipe:0",  # Read video input from stdin
            "-ar", "44100",
            "-ac", "1",
            "-f", "s16le",
            "-i", "pipe:3",  # Read audio input from stdin
            "-c:v", "libx264",
            "-b:v", "1500k",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-g", "120",  # Set keyframe interval to 4 seconds (assuming 30 frames/second)
            "-f", "flv",
            self.stream_url
        ]
        while True:
            try:
                # Open the subprocess with stdin and stderr pipes
                self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

                if self._connection_is_alive():
                    break
                else:
                    return self.reconnect()
            except Exception as e:
                print(f"Error starting ffmpeg process: {e}")
            
            # Sleep for a short duration before the next check
            time.sleep(5)
    
    def _read_stderr(self):
        while True:
            line = self.process.stderr.readline().decode("utf-8")
            if not line:
                break
            print(line.strip()) 


    def send_video(self, video_chunk):
        try:
            self.process.stdin.write(video_chunk)
            self.process.stdin.flush()  # Ensure data is sent immediately
        except BrokenPipeError:
            print("Error: Broken pipe. Reconnecting...")
            self.reconnect()

    def send_audio(self, audio_chunk):
        try:
            self.process.stdin.write(audio_chunk)
            self.process.stdin.flush()  # Ensure audio data is sent immediately
        except BrokenPipeError:
            print("Error: Broken pipe. Reconnecting...")
            self.reconnect()

    def disconnect(self):
        # Terminate the ffmpeg process
        try:
            if self.process.poll() is None:
                self.process.terminate()
        except Exception as e:
            print(f"Error terminating ffmpeg process: {e}")

    def reconnect(self):
        # Close the existing ffmpeg process
        if self.process.poll() is None:
            self.process.terminate()

        # Reconnect and start a new ffmpeg process
        self.connect()

    def _connection_is_alive(self):
        try:
            sock = socket.create_connection(("a.rtmp.youtube.com", 1935), timeout=10)
            sock.sendall(b" ")
            sock.close()
            return True
        except Exception:
            print("Error: Connection lost. Reconnecting...")
            return False


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


class CameraHandler(StreamHandler):
    def __init__(self, camera_location="/dev/video0", num_of_frames=60):
        self.camera_location = camera_location
        self.num_of_frames = num_of_frames
        self.camera_stream = None
        self.initialize_camera()

    def grant_camera_permissions(self):
        try:
            # Add the current user to the 'video' group to grant camera access
            os.system("sudo usermod -aG video $(whoami)")
        except Exception as e:
            print(f"Error granting camera permissions: {e}")
    
    def initialize_camera(self):
        self.camera_stream = cv2.VideoCapture(self.camera_location)
        if not self.camera_stream.isOpened():
            print("Error: Could not open camera. Please check camera connection and permissions.")
            self.camera_stream = None   
            self.grant_camera_permissions()

    def get(self):
        """Send a video chunk"""
        frame_list = self.get_frame_list()
        video_chunk = self.create_video_chunk(frame_list)
        return video_chunk

    def get_frame_list(self):
        frame_list = []
        if self.camera_stream is not None:
            attempts = 0
            while len(frame_list) < self.num_of_frames and attempts < 3:
                ret, frame = self.camera_stream.read()
                if ret:
                    frame_list.append(frame)
                else:
                    print("Warning: Failed to retrieve frame. Retrying...")
                    time.sleep(1)  # Wait for a moment before retrying
                    attempts += 1
            if len(frame_list) < self.num_of_frames:
                print("Error: Unable to capture enough frames from the camera.")
        else:
            self.initialize_camera()
            print("Error: Camera not initialized. Please check camera connection and permissions.")
            return self.get_frame_list()
        return frame_list
    
  
    def create_video_chunk(self, frame_list):
        """Create a video chunk from a frame list"""
        # Get the height and width of the frames (assuming all frames have the same dimensions)
        height, width, layers = frame_list[0].shape

        # Define the codec for encoding frames
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Create a VideoWriter object with memory as the output (in-memory VideoWriter)
        video_chunk_bytes_io = io.BytesIO()

        # Write frames to the in-memory VideoWriter object
        writer = cv2.VideoWriter("output.mp4", fourcc, 30, (width, height), isColor=True)
        for frame in frame_list:
            if frame is not None:
                writer.write(frame)

        writer.release()

        # Get the video chunk as bytes from the in-memory VideoWriter object


        video_chunk_bytes_io.write(open("output.mp4", "rb").read())
        
        return video_chunk_bytes_io.getvalue()



    def quit(self):
        if self.camera_stream is not None:
            self.camera_stream.release()

    def reconnect_camera(self):
        self.quit()
        self.initialize_camera()


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
        


def main():
    streamer = Streamer()
    livestream_client = LiveStream(broadcast_key='um42-gd7r-hke8-xagh-dwgr')
    streamer.add_client(livestream_client)
    streamer.initialize()
    streamer.start_stream()


if __name__ == "__main__":
    main()