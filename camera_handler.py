import os
import time
import io
import cv2
from stream_handler import StreamHandler


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