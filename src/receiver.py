import random
from tkinter import *
import tkinter.messagebox
import hashlib
import time
import os
import pyaudio
import wave
import threading
from FSK import modulation, demodulation
from utils import *


class Receiver:
    def __init__(self, args):
        self.args = args
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.save_place = 'output.wav'

    def start_record(self):
        '''
        描述：开始录音
        参数：无
        返回：无
        '''
        self.label1["text"] = "正在录音中"
        threading._start_new_thread(self.recording, ())

    def recording(self):
        '''
        描述：录音
        参数：无
        返回：无
        '''
        self.running = True
        self.frames = []
        recorder = pyaudio.PyAudio()
        stream = recorder.open(format = self.format,
                        channels = self.args.nchannels,
                        rate = self.args.framerate,
                        input = True,
                        frames_per_buffer = self.chunk)
        while(self.running):
            data = stream.read(self.chunk)
            self.frames.append(data)
 
        stream.stop_stream()
        stream.close()
        recorder.terminate()
 
    def stop_record(self):
        '''
        描述：停止录音
        参数：无
        返回：无
        '''
        self.label1["text"] = "未开始录音"
        self.running = False
        self.save_wave()
        self.get_result()

    def save_wave(self):
        '''
        描述：保存录音结果
        参数：无
        返回：无
        '''
        p = pyaudio.PyAudio()            
        filename = os.path.join(self.args.save_base_receive, self.save_place)               
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.args.nchannels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.args.framerate)
        wf.writeframes(b''.join(self.frames))
        wf.close()


    def get_result(self):
        '''
        描述：解析并获取录音结果
        参数：无
        返回：无
        '''
        get_wave = load_wave(save_base = self.args.save_base_receive, file_name = self.save_place)
        get_seq = demodulation(self.args, get_wave)
        packet, place = divide_packets(self.args, get_seq)
        result = string_decode(packet)

        tkinter.messagebox.showinfo('传输结果', result)
        

    def init_ui(self):
        '''
        描述：初始化gui
        参数：无
        返回：无
        '''
        self.window = Tk()
        self.label1 = Label(self.window, text="未开始录音")
        self.label1.grid(row = 0, column = 0, stick = W, pady = 10)
        self.button1 = Button(self.window, text='开始录音', command = self.start_record)
        self.button1.grid(row = 1, column = 0, stick = W, pady = 10)
        self.button2 = Button(self.window, text='结束录音', command = self.stop_record)
        self.button2.grid(row = 1, column = 1, stick = W, pady = 10)
        self.window.mainloop()



if __name__ == "__main__":
    args = init_args()
    receiver = Receiver(args)
    receiver.init_ui()