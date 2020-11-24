import wave
import os
import numpy as np
import random
from scipy.io import wavfile
import struct
import matplotlib.pyplot as plt
from scipy import signal
import argparse

def init_args():
    '''
    描述：加载全局设置---窗口长度，0和1对应的频率，采样频率振幅等其他参数
    参数：无
    返回：args变量，对应全局设置
    '''
    parser = argparse.ArgumentParser(description="Choose the parameters")

    #0和1的频率
    parser.add_argument("--frequency_0", type = int, default = 10000)
    parser.add_argument("--frequency_1", type = int, default = 20000)

    #采样频率，振幅，宽度等通用设置
    parser.add_argument("--framerate", type = int, default = 48000)
    parser.add_argument("--sample_width", type = int, default = 2)
    parser.add_argument("--nchannels", type = int, default = 1)
    parser.add_argument("--volume", type = float, default = 1000.0)
    parser.add_argument("--start_place", type = int, default = 0)

    #单个窗口的长度(单位秒)
    parser.add_argument("--window_length", type = float, default = 0.01)

    #一个包最长长度(多少个比特)
    parser.add_argument("--packet_length", type = float, default = 1000)

    #保存和接收的文件夹名称
    parser.add_argument("--save_base_send", type = str, default = 'send')
    parser.add_argument("--save_base_receive", type = str, default = 'receive')
    args = parser.parse_args()
    return args

def save_wave(my_wave, framerate = 44100, sample_width = 2, nchannels = 1, save_base = 'sound', file_name = 'pulse.wav'):
    '''
    描述：存储wav文件
    参数：波，帧率，采样宽度， 通道数，文件夹名，文件名
    返回：无
    '''
    the_place = os.path.join(save_base, file_name)
    wf = wave.open(the_place, 'wb')
    wf.setnchannels(nchannels)
    wf.setframerate(framerate)
    wf.setsampwidth(sample_width)
    for i in range(len(my_wave)):
        the_result = int(my_wave[i]) 
        data = struct.pack('<h', the_result)
        wf.writeframesraw(data)
    wf.close()


def load_wave(save_base = 'sound', file_name = 'pulse.wav'):
    '''
    描述：读取wav文件
    参数：文件夹名，文件名, 帧数，帧率，采样时间，长度
    返回：y
    '''
    the_place = os.path.join(save_base, file_name)
    file = wave.open(the_place)
    n_frames = file.getparams().nframes  # 帧总数
    framerate = file.getparams().framerate  # 采样频率
    sample_time = 1 / framerate  # 采样点的时间间隔
    duration = n_frames / framerate  # 声音信号的长度

    frequency, audio_sequence = wavfile.read(the_place)
    x_seq = np.arange(0, duration, sample_time)
    print("n_frames:", n_frames)
    print("framerate:", framerate)
    print("sample_time:", sample_time)
    print("duration:", duration)
    print("frequency:", frequency)
    y = audio_sequence  
    return y

def generate_random_seq(length):
    '''
    描述：生成随机0-1序列
    参数：长度
    返回：随机0-1序列
    '''
    original_seq = []
    for i in range(length):
        num = round(random.random())
        original_seq.append(num)
    return original_seq

def compare_seqs(original_seq, get_seq):
    '''
    描述：比较两个seq是否一样
    参数：原先和获取的seq
    返回：正确/错误
    '''
    if len(original_seq) != len(get_seq):
        return False
    for i in range(len(original_seq)):
        if original_seq[i] != get_seq[i]:
            return False
    return True