import random
from tkinter import *
import tkinter.messagebox
import hashlib
import time
from FSK import modulation, demodulation
from utils import *


class Sender:
    def __init__(self, args):
        self.args = args
        
    def send_signal(self):
        '''
        描述：保存音频文件
        参数：无
        返回：无
        '''
        seq = self.entry1.get()
        save_place = self.entry2.get()
        if len(seq) == 0:
            tkinter.messagebox.showinfo('错误','待传输信息不能为空！')
            return
        if len(save_place) == 0:
            tkinter.messagebox.showinfo('错误','保存的位置不能为空！')
            return
        
        # original_seq = string_encode(seq)
        # original_seq = np.append(args.preamble, np.zeros(100))
        # original_seq = self.args.preamble + original_seq
        original_seq = encode_bluetooth_packet(args, seq)
        save_place += '.wav'
        print("The original seq is:\n", original_seq)

        the_wave = modulation(self.args, original_seq)
        save_wave(the_wave, framerate = self.args.framerate, sample_width = self.args.sample_width, nchannels = self.args.nchannels,
            save_base = self.args.save_base_send, file_name = save_place)
        self.window.destroy()

    def init_ui(self):
        '''
        描述：初始化gui
        参数：无
        返回：无
        '''
        self.window = Tk()
        self.label1 = Label(self.window, text="请输入数据")
        self.label1.grid(row = 0, column = 0, stick = W, pady = 10)
        self.entry1 = Entry(self.window, width = 100)
        self.entry1.grid(row = 0, column = 1, stick = W, pady = 10)
        self.label2 = Label(self.window, text="请输入文件名（不含.wav）")
        self.label2.grid(row = 1, column = 0, stick = W, pady = 10)
        self.entry2 = Entry(self.window, width = 100)
        self.entry2.grid(row = 1, column = 1, stick = W, pady = 10)
        self.button = Button(self.window, text='确定', command = self.send_signal)
        self.button.grid(row = 2, column = 1, stick = W, pady = 10)
        self.window.mainloop()



if __name__ == "__main__":
    args = init_args()
    sender = Sender(args)
    sender.init_ui()