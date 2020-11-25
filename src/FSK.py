import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import load_wave, save_wave, init_args, generate_random_seq, compare_seqs, string_encode, string_decode, divide_packets, windowed_fft

def generate_pulse(framerate, frequency, volume, start_place, duration):
    '''
    描述：生成脉冲信号
    参数：帧率，频率，振幅，相位，时长
    返回：波形
    '''
    n_frames = round(duration * framerate)
    x = np.linspace(0, duration, num = n_frames)
    y = np.sin(2 * np.pi * frequency * x + start_place) * volume
    return y

def modulation(args, bits):
    '''
    描述：FSK调制算法
    参数：全局参数, 0-1比特信号（规定比特信号长度小于等于一个包的限制）
    返回：得到的波---numpy格式的一维数组
    '''
    result_wave = np.empty(shape = (1, 0))
    for bit in bits:
        if bit == 0:
            frequency = args.frequency_0
        else: 
            frequency = args.frequency_1
        y = generate_pulse(args.framerate, frequency, args.volume, args.start_place, args.window_length)
        result_wave = np.append(result_wave, y)
    return result_wave

def get_dominate_frequency(args, wave):
    '''
    描述：获取一个区间内主导性频率(0的还是1的)
    参数：全局参数，区间的波形（numpy格式一维数组）
    返回：结果
    '''
    fourier_result = windowed_fft(wave)
    size_0 = fourier_result[round(args.frequency_0 / args.framerate * len(fourier_result))]
    size_1 = fourier_result[round(args.frequency_1 / args.framerate * len(fourier_result))]
    if size_0 > size_1:
        return 0
    else: 
        return 1

def demodulation(args, wave):
    '''
    描述：FSK解调算法
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特信号
    '''
    result = []
    window_length = round(args.framerate * args.window_length)
    start_place = 0
    while start_place < len(wave):
        if start_place + window_length <= len(wave):
            length = window_length
        else: 
            length = len(wave) - start_place
            
        sub_wave = wave[start_place: start_place + length - 1]
        dominate = get_dominate_frequency(args, sub_wave)
        result.append(dominate)
        start_place += length

    return result

if __name__ == '__main__':


    args = init_args()
    original_info = '绿罗马帝国强大！1453征服拜占庭！Ceddin deden， neslin baban！'
    original_seq = string_encode(original_info)
    original_seq = args.preamble + original_seq

    #the_wave = modulation(args, original_seq)
    #save_wave(the_wave, framerate = args.framerate, sample_width = args.sample_width, nchannels = args.nchannels, save_base = 'send', file_name = 'kebab.wav')
    
    get_wave = load_wave(save_base = 'receive', file_name = 'output.wav')
    #get_wave = load_wave(save_base = 'send', file_name = 'kebab.wav')
    get_seq = demodulation(args, get_wave)
    packet, place = divide_packets(args, get_seq)
    result = string_decode(packet)
    print(original_info)
    print(result)
    print(place)
    