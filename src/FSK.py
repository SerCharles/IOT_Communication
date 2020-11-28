import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import load_wave, save_wave, init_args, generate_random_seq, compare_seqs, string_encode, string_decode, divide_packets, windowed_fft
import statsmodels.tsa.api as smt 

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


def get_window_start(args, wave):
    '''
    描述：用前导码对齐窗口
    参数：全局参数，波---numpy格式的一维数组
    返回：前导码在哪？
    '''
    preamble_seq = modulation(args, args.preamble)
    length = len(wave)
    length_preamble = len(preamble_seq)
    start = 0
    correlates = []
    real_wave_start_place = -1
    while start + length_preamble <= length:
        the_wave = wave[start : start + length_preamble]
        correlate = np.dot(the_wave, preamble_seq)
        if(abs(correlate) >= args.threshold and real_wave_start_place == -1):
            real_wave_start_place = start
        correlates.append(correlate)
        start += 1
    place = real_wave_start_place + np.argmax(correlates[real_wave_start_place:real_wave_start_place+4000])
    print(place)
    plt.plot(correlates)
    plt.show()
    return place


def demodulate_one(args, wave):
    '''
    描述：获取主导频率来解码一个bit
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特
    '''
    fourier_result = np.abs(np.fft.fft(wave))
    #plt.plot(fourier_result)
    #plt.show()
    length = len(fourier_result)
    fourier_result = fourier_result[0 : length // 2]
    max_place = np.argmax(fourier_result)
    max_frequency = round(max_place * args.framerate / length)
    dist_0 = abs(max_frequency - args.frequency_0)
    dist_1 = abs(max_frequency - args.frequency_1)
    if dist_0 < dist_1:
        return 0
    else: 
        return 1


def demodulation(args, wave):
    '''
    描述：FSK解调算法
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特信号
    '''
    length_one = round(args.framerate * args.window_length)
    length = len(wave)
    start = 0
    result = []
    while(start + length_one <= length):
        sub_wave = wave[start : start + length_one]
        the_bit = demodulate_one(args, sub_wave)
        result.append(the_bit)
        start += length_one
    return result

if __name__ == '__main__':


    args = init_args()
    original_info = '绿罗马帝国强大！1453征服拜占庭！Ceddin deden， neslin baban！'
    original_seq = string_encode(original_info)
    original_seq = args.preamble + original_seq
    #the_wave = modulation(args, original_seq)
    #save_wave(the_wave, framerate = args.framerate, sample_width = args.sample_width, nchannels = args.nchannels, save_base = 'send', file_name = 'kebab.wav')
    #get_wave = load_wave(save_base = 'send', file_name = 'kebab.wav')
    #get_wave = np.append(np.zeros(100000), get_wave)
    get_wave = load_wave(save_base = 'receive', file_name = 'output.wav')
    place = get_window_start(args, get_wave)
    get_seq = demodulation(args, get_wave[place:])
    get_seq = get_seq[ : len(original_seq)]
    error = np.sum(get_seq != original_seq) / len(original_seq)
    print("{:.4f}%".format(error * 100))


    packet, place = divide_packets(args, get_seq)
    result = string_decode(packet)
    print(original_info)
    print(result)
    