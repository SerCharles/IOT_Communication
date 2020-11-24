import numpy as np
from scipy import signal


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
    返回：得到的波
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




