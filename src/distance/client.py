import argparse
import os
import random
import wave

import requests
import threading
import pyaudio

from utils import init_args


class RecorderThread(threading.Thread):
    def __init__(self, filename, self_args, client):
        threading.Thread.__init__(self)
        self.recording = False
        self.args = self_args
        self.filename = filename
        self.client = client

    def run(self):
        self.recording = True
        frames = []
        recorder = pyaudio.PyAudio()
        stream = recorder.open(format=self.args.format,
                               channels=self.args.channels,
                               rate=self.args.framerate,
                               input=True,
                               frames_per_buffer=self.args.chunk)
        while self.recording:
            data = stream.read(self.args.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        recorder.terminate()

        p = pyaudio.PyAudio()
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.args.channels)
        wf.setsampwidth(p.get_sample_size(self.args.format))
        wf.setframerate(self.args.framerate)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.client.upload(self.filename)


class DistanceClient(object):

    def __init__(self, url, side, args):
        if side not in ["a", "b"]:
            raise Exception("unknown side! must be one of 'a', 'b'")
        self.side = side
        self.url = url
        self.recording = False
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.framerate = 44100
        self.offset_a = 1
        self.offset_b = 3
        self.audio_len = 0.5
        self.record_len = 5
        self.args = args

    def upload(self, filename):
        resp = requests.post(self.url.replace("<side>", self.side),
                             files={"file": open(filename, "rb")})
        print(resp)

    def start_record(self):
        filename = self.side + "_" + random.randint(0, 255) + ".wav"
        thread = RecorderThread(filename, self.args, self)
        thread.start()

    def start(self):
        while True:
            line = input("Press enter to start a recording")
            self.start_record()
            if line == "exit":
                break


if __name__ == "__main__":
    args = init_args()
    DistanceClient(args).start()

