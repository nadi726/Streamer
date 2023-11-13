
import threading
import cv2
from events import EventEmitter


class CameraHandler:
    def __init__(self, camera_location="/dev/video1", num_of_frames=30):
        self.camera_location = camera_location
        self.num_of_frames = num_of_frames
        self.camera_stream = None
        self.thread = None
        self.camera_stream = cv2.VideoCapture(self.camera_location)
        if not self.camera_stream.isOpened():
            print("Error: Could not open camera. Please check camera connection and permissions.")
            self.camera_stream = None   
        self.thread = threading.Thread(target=self.get_frame_thread)
                
    def get_frame_thread(self):
        while True:
            ret, frame = self.camera_stream.read()
            # Encode the frame as JPEG image (you can choose other formats like PNG as well)
            if ret:
                retval, buffer = cv2.imencode('.jpg', frame)

                # Check if the encoding was successful
                if retval:
                    # Convert the buffer (array) to bytes
                    frame_bytes = buffer.tobytes()
                    EventEmitter.trigger_frame_event(frame_bytes)
                else:
                    print("Error: Could not encode the frame.")

    def start_thread(self):
        self.thread.start()


if __name__ == "__main__":
    handler = CameraHandler()