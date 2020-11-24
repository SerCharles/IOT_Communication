import numpy as np
from scipy import signal
from utils import load_wave, save_wave, init_args, generate_random_seq, compare_seqs

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
    描述：获取一个区间内主导性频率
    参数：全局参数，区间的波形（numpy格式一维数组）
    返回：主导频率
    '''
    fourier_result = abs(np.fft.fft(wave))
    index = np.argmax(fourier_result)
    frequency = round(index / len(fourier_result) * args.framerate)
    return frequency

def demodulation(args, wave):
    '''
    描述：FSK解调算法
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特信号
    '''
    result = []
    window_length = round(args.framerate * args.window_length)
    threshold = 0.1 #如果窗口太小了就不考虑了
    frequency_range = [0.9, 1.1]
    start_place = 0
    while start_place < len(wave):
        if start_place + window_length <= len(wave):
            length = window_length
        else: 
            length = window_length - start_place
        if length < window_length * threshold:
            continue
        
        sub_wave = wave[start_place: start_place + length - 1]
        dominate_frequency = get_dominate_frequency(args, sub_wave)
        if dominate_frequency >= args.frequency_0 * frequency_range[0] and dominate_frequency <= args.frequency_0 * frequency_range[1]:
            result.append(0)
        elif dominate_frequency >= args.frequency_1 * frequency_range[0] and dominate_frequency <= args.frequency_1 * frequency_range[1]:
            result.append(1)
        start_place += window_length
    return result

if __name__ == '__main__':
    args = init_args()
    original_seq = generate_random_seq(300)
    print("The original seq is:\n", original_seq)

    the_wave = modulation(args, original_seq)
    save_wave(the_wave, framerate = args.framerate, sample_width = args.sample_width, nchannels = args.nchannels, save_base = 'send', file_name = 'kebab.wav')
    get_wave = load_wave(save_base = 'send', file_name = 'kebab.wav')
    get_seq = demodulation(args, get_wave)
    print("The loaded seq is:\n", get_seq)

    result = compare_seqs(original_seq, get_seq)
    if result:
        print("The original seq and the seq I get is identical, right!")
    else: 
        print("The original seq and the seq I get is not identical, wrong!")
    