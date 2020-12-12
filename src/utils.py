import wave
import os
import numpy as np
import random
from scipy.io import wavfile
import struct
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import csv


def init_args():
    """
    描述：加载全局设置---窗口长度，0和1对应的频率，采样频率振幅等其他参数
    参数：无
    返回：args变量，对应全局设置
    """
    parser = argparse.ArgumentParser(description="Choose the parameters")

    # 0和1的频率
    parser.add_argument("--frequency_0", type=int, default=4000)
    parser.add_argument("--frequency_1", type=int, default=6000)

    # 采样频率，振幅，宽度等通用设置
    parser.add_argument("--framerate", type=int, default=48000)
    parser.add_argument("--sample_width", type=int, default=2)
    parser.add_argument("--nchannels", type=int, default=1)
    parser.add_argument("--volume", type=float, default=20000.0)
    parser.add_argument("--start_place", type=int, default=0)

    # 单个窗口的长度(单位秒)
    parser.add_argument("--window_length", type=float, default=2.5e-2)

    # 一个包最长长度(多少个比特)
    parser.add_argument("--packet_length", type=int, default=1000)

    # 保存和接收的文件夹名称
    parser.add_argument("--save_base_send", type=str, default='send')
    parser.add_argument("--save_base_receive", type=str, default='receive')
    parser.add_argument("--original_place", type=str, default='content.csv')

    # 包长度是几个bit
    parser.add_argument("--packet_head_length", type=int, default=8)

    #beep-beep
    parser.add_argument("--sound_velocity", type=int, default=343)
    parser.add_argument("--server_url", type=str, default="http://localhost:5000/iot/<side>")
    parser.add_argument("--side", type=str, default="a")
    parser.add_argument("--delay_a", type=int, default=1)
    parser.add_argument("--delay_b", type=int, default=3)
    parser.add_argument("--record_len", type=int, default=5)
    parser.add_argument("--beep_wave", type=str, default="distance/beep.wav")
    parser.add_argument("--beep_beep", type=bool, default=False)

    #测不测试（是否显示图啥的）
    parser.add_argument("--test", type = int, default = 0)
    args = parser.parse_args()

    # 前导码
    args.preamble = [0, 1] * 10

    # 解码用
    args.threshold = 2e11
    return args


def save_wave(my_wave, framerate=44100, sample_width=2, nchannels=1, save_base='sound', file_name='pulse.wav'):
    """
    描述：存储wav文件
    参数：波，帧率，采样宽度， 通道数，文件夹名，文件名
    返回：无
    """
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


def load_wave(save_base='sound', file_name='pulse.wav'):
    """
    描述：读取wav文件
    参数：文件夹名，文件名, 帧数，帧率，采样时间，长度
    返回：y
    """
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
    """
    描述：生成随机0-1序列
    参数：长度
    返回：随机0-1序列
    """
    original_seq = []
    for i in range(length):
        num = round(random.random())
        original_seq.append(num)
    return original_seq


def compare_seqs(original_seq, get_seq):
    """
    描述：比较两个seq是否一样
    参数：原先和获取的seq
    返回：正确/错误
    """
    if len(original_seq) != len(get_seq):
        return False
    for i in range(len(original_seq)):
        if original_seq[i] != get_seq[i]:
            return False
    return True


def string_encode(string):
    """
    描述：将中英文字符串编码成0-1序列
    参数：中英文混杂的字符串（已经按照大小分包）
    返回：0-1序列数组
    """
    byte_list = str.encode(string, encoding="utf-8")
    bit_list = []
    for byte in byte_list:
        for i in range(8):
            num = (byte >> (7 - i)) & 1
            bit_list.append(num)
    return bit_list


def string_decode(bit_list):
    """
    描述：将0-1序列解码为中英文字符串
    参数：0-1序列数组（已经去除前导码和包头）
    返回：中英文字符串
    """
    byte_list = []
    length = len(bit_list)

    # 补0
    if length % 8 != 0:
        for i in range(8 - (length % 8)):
            bit_list.append(0)

    # 解析
    start = 0
    while start < len(bit_list):
        the_byte_list = bit_list[start: start + 8]
        the_num = 0
        for i in range(8):
            the_num += the_byte_list[i] << (7 - i)
        # the_byte = chr(the_num)
        byte_list.append(the_num)
        start += 8
    byte_list = bytes(byte_list)
    result = bytes.decode(byte_list, encoding="utf-8")
    return result


def bit_to_int(seq):
    '''
    描述：把八bit二进制转化成数字
    参数：二进制
    返回：数字
    '''
    if len(seq) > 8:
        seq = seq[: 8]
    elif len(seq) < 8:
        for i in range(8 - len(seq)):
            seq.append(0)
    num = 0
    for i in range(8):
        num += (seq[7 - i] << i)
    return num


def int_to_bit(num):
    '''
    描述：把数字转化成八bit二进制
    参数：数字
    返回：二进制
    '''
    seq = []
    for i in range(8):
        seq.append((num >> (7 - i)) & 1)
    return seq


def get_original_seq(args):
    '''
    描述：返回original seq
    参数：全局参数
    返回：original seq
    '''
    original_seq = []
    with open(args.original_place, 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
        for i in range(5, len(result)):
            seq = []
            for j in range(4, len(result[i])):
                try:
                    seq.append(int(result[i][j]))
                except:
                    pass
            original_seq.append(seq)
    return original_seq


def get_accuracy(original_seq, get_seq):
    '''
    描述：计算准确率
    参数：原始信号，新的信号
    返回：无
    '''
    length = min(len(original_seq), len(get_seq))
    correct = 0
    for i in range(length):
        if (original_seq[i] == get_seq[i]):
            correct += 1
    accuracy = correct / len(original_seq)
    return accuracy


def encode_bluetooth_packet(args, seq):
    '''
    TODO：蓝牙包编码
    描述：生成蓝牙包
    参数：全局参数，0-1序列
    返回：完整的蓝牙包(0-1序列)(包括分包)
    '''
    encoded_seq = string_encode(seq)
    encoded_len = len(encoded_seq)
    packet_payload_len = 40
    packets_cnt = int(encoded_len / packet_payload_len) if encoded_len % packet_payload_len == 0 \
        else int(encoded_len / packet_payload_len) + 1
    blank_len = 10
    bluetooth_packets_seq = []
    bluetooth_packets_seq += ([0] * blank_len)
    # 分包
    for i in range(packets_cnt):
        bluetooth_packets_seq += args.preamble
        bluetooth_packets_seq += (int_to_bit(packet_payload_len if i != packets_cnt - 1
                                             else encoded_len - i * packet_payload_len))
        bluetooth_packets_seq += (encoded_seq[i * packet_payload_len: min((i + 1) * packet_payload_len, encoded_len)])
        bluetooth_packets_seq += ([0] * blank_len)

    return bluetooth_packets_seq


def decode_bluetooth_packet(args, packets):
    '''
    TODO：蓝牙包解码
    描述：将整个蓝牙包进行拆分
    参数：全局参数，蓝牙包
    返回：经过修正后的内容
    '''
    seq = []
    for packet in packets:
        seq += packet
    return string_decode(seq)
