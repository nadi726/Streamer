from livestream import LiveStream
from streamer import Streamer


def main():
    streamer = Streamer()
    livestream_client = LiveStream(broadcast_key='um42-gd7r-hke8-xagh-dwgr')
    streamer.set_client(livestream_client)
    streamer.initialize()
    streamer.start_stream()


if __name__ == "__main__":
    main()