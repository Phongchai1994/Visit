import threading
import winsound

class PlaySound(threading.Thread):
    def __init__(self, wav_path):
        super().__init__()
        self.wav_path = wav_path

    def run(self):
        winsound.PlaySound(self.wav_path, winsound.SND_FILENAME)
