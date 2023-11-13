
from camera_handler import CameraHandler
from audio_handler import AudioHandler
from events import EventEmitter
from streamer import Streamer
from wav_writer import WavWriter


def main():
    stream_instance = Streamer(broadcast_key='um42-gd7r-hke8-xagh-dwgr')
    audio_file = WavWriter()
    EventEmitter.add_frame_listener(stream_instance)
    EventEmitter.add_audio_listener(stream_instance)
    EventEmitter.add_audio_listener(audio_file)

    camera_handler = CameraHandler()
    audio_handler = AudioHandler()
    camera_handler.start_thread()
    audio_handler.start_thread()

if __name__ == "__main__":
    main()