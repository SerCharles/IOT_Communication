# -*- coding: utf-8 -*-
import os
import random
import threading
import time
import wave

import pyaudio
import requests

from utils import init_args


class RecorderThread(threading.Thread):
    def __init__(self, filename, self_args, client):
        threading.Thread.__init__(self)
        self.recording = False
        self.args = self_args
        self.filename = filename
        self.client = client
        self.chunk = 1024
        self.format = pyaudio.paInt16

    def run(self):
        self.recording = True
        frames = []
        recorder = pyaudio.PyAudio()
        stream = recorder.open(format=self.format,
                               channels=self.args.nchannels,
                               rate=self.args.framerate,
                               input=True,
                               frames_per_buffer=self.chunk)
        start_time = time.time()
        while self.recording and (time.time() - start_time < self.args.record_len):
            data = stream.read(self.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        recorder.terminate()

        p = pyaudio.PyAudio()
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.args.nchannels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.args.framerate)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.client.upload(self.filename)
        try:
            os.remove(self.filename)
        except:
            pass


class DistanceClient(object):

    def __init__(self, url, side, args):
        if side not in ["a", "b"]:
            raise Exception("unknown side! must be one of 'a', 'b'")
        self.side = side
        self.url = url
        self.recording = False
        self.format = pyaudio.paInt16
        self.channels = args.nchannels
        self.framerate = args.framerate
        self.args = args
        self.wave_file = wave.open(self.args.beep_wave, 'rb')
        chunks = []
        data = self.wave_file.readframes(1024)
        while data != b'':
            chunks.append(data)
            data = self.wave_file.readframes(1024)
        data = b''.join(chunks)
        self.data = data

    def upload(self, filename):
        resp = requests.post(self.url.replace("<side>", self.side),
                             files={"file": open(filename, "rb")})
        if resp.status_code == 200:
            print(filename, "uploaded")
        else:
            print(filename, "failed to upload")

    def start_record(self):
        filename = os.path.join("receive", self.side + "_" + str(random.randint(0, 255)) + ".wav")
        thread = RecorderThread(filename, self.args, self)
        thread.start()
        return filename

    def play_beep(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(self.wave_file.getsampwidth()),
                        channels=self.wave_file.getnchannels(),
                        rate=self.wave_file.getframerate(), output=True)
        stream.write(self.data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start(self):
        while True:
            print("Press enter to start recording")
            line = input("")
            filename = self.start_record()
            print("Recording", filename, "started")
            if self.side == 'a':
                time.sleep(self.args.delay_a)
            else:
                time.sleep(self.args.delay_b)
            self.play_beep()
            if line == "exit":
                break


def main():
    args = init_args()
    if args.side != 'a' and args.side != 'b':
        print("Side must be 'a' or 'b'")
        return
    print("Server url:", args.server_url)
    print("You are side", args.side)
    DistanceClient(args.server_url, args.side, args).start()


if __name__ == "__main__":
    main()
