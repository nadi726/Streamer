
from stream_client import StreamClient
import subprocess
import time
import socket


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

    def _connection_is_alive(self):
        try:
            sock = socket.create_connection(("a.rtmp.youtube.com", 1935), timeout=10)
            sock.sendall(b" ")
            sock.close()
            return True
        except Exception:
            print("Error: Connection lost. Reconnecting...")
            return False
