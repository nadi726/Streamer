import socket
import subprocess
import time
from events import AudioListener, FrameListener


class Streamer(FrameListener, AudioListener):
    YOUTUBE_ENDPOINT = "rtmp://a.rtmp.youtube.com/live2"
    
    def __init__(self, broadcast_key):
        self.stream_url = f"{self.YOUTUBE_ENDPOINT}/{broadcast_key}"
        self.process = None
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

            except Exception as e:
                print(f"Error starting ffmpeg process: {e}")

            if self._connection_is_alive():
                break
            else:
                # Sleep for a short duration before retrying
                time.sleep(5)
                return self.reconnect()

    def disconnect(self):
        """Terminate the ffmpeg process"""
        try:
            if self.process.poll() is None:
                self.process.terminate()
        except Exception as e:
            print(f"Error terminating ffmpeg process: {e}")

    def reconnect(self):   
        self.disconnect()
        self.connect()
           
    def on_frame(self,data):
        if self.process is None or self.process.poll() is not None:
            self.connect()
        
        try:
            self.process.stdin.write(data)
            self.process.stdin.flush()  # Ensure data is sent immediately
          
        except BrokenPipeError as e:
            print(f"-On frame- Error: Broken pipe. Reconnecting... ({e})")
            self.reconnect()

    def on_audio(self, data):
        if self.process is None or self.process.poll() is not None:
            self.connect()
        
        try:
  
            self.process.stdin.writable(data)
            self.process.stdin.flush()  # Ensure audio data is sent immediately
        except BrokenPipeError as e:
            print(f"-On audio- Error: Broken pipe. Reconnecting... ({e})")
            self.reconnect()
            
    def _connection_is_alive(self):
        try:
            sock = socket.create_connection(("a.rtmp.youtube.com", 1935), timeout=10)
            sock.sendall(b" ")
            sock.close()
            return True
        except Exception:
            print("Error: Connection lost. Reconnecting...")
            return False()