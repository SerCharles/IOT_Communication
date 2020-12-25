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

    def get_result(self):
        """
        描述：解析并获取录音结果
        参数：无
        返回：无
        """
        start = time.time_ns()
        get_wave = load_wave(save_base=self.args.save_base_receive, file_name=self.entry.get()+'.wav')
        end = time.time_ns()
        print('读取文件耗时：', (end-start)/1e6, 'ms')
        if len(get_wave.shape) == 2:
            get_wave = get_wave[:, 0]

        start = time.time_ns()
        packets = demodulation(self.args, get_wave)
        count, result = decode_bluetooth_packet(self.args, packets)
        end = time.time_ns()
        print('解码文本耗时：', (end-start)/1e6, 'ms')
        # tkinter.messagebox.showinfo('传输结果', '蓝牙包成功解码数量：{}\n解码信息：{}'
        #                             .format(count, result))

        answer_wave = load_wave(save_base=self.args.save_base_send, file_name='test.wav')
        if len(get_wave.shape) == 2:
            answer_wave = answer_wave[:, 0]
        answer_packets = demodulation(self.args, answer_wave)
        answer_count, answer_result = decode_bluetooth_packet(self.args, answer_packets)
        bit_count = 0
        bit_right = 0
        for packet_tuple, answer_packet_tuple in zip(packets, answer_packets):
            packet = packet_tuple[0]
            answer_packet = answer_packet_tuple[0]
            for i, j in zip(packet, answer_packet):
                bit_right += (i == j)
            bit_count += len(answer_packet)
            print(len(packet), len(answer_packet))
            print(packet)
            print(answer_packet)
        tkinter.messagebox.showinfo('传输结果', '蓝牙包成功解码数量：{}/{}\n解码信息：{}\n实际信息：{}\n比特正确率：{:.4f}'
                                    .format(count, answer_count, result, answer_result, bit_right/bit_count))

    def init_ui(self):
        """
        描述：初始化gui
        参数：无
        返回：无
        """
        self.window = Tk()
        self.label = Label(self.window, text="请输入待解码文件名（不含.wav）")
        self.label.grid(row=1, column=0, stick=W, pady=10)
        self.entry = Entry(self.window, width=100)
        self.entry.grid(row=1, column=1, stick=W, pady=10)
        self.button = Button(self.window, text='确定', command=self.get_result)
        self.button.grid(row=2, column=1, stick=W, pady=10)
        self.window.mainloop()


if __name__ == "__main__":
    args = init_args()
    receiver = Receiver(args)
    receiver.init_ui()
