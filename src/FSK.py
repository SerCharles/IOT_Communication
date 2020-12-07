import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import *
import statsmodels.tsa.api as smt


def generate_pulse(framerate, frequency, volume, start_place, duration):
    """
    描述：生成脉冲信号
    参数：帧率，频率，振幅，相位，时长
    返回：波形
    """
    n_frames = round(duration * framerate)
    x = np.linspace(0, duration, num=n_frames)
    y = np.sin(2 * np.pi * frequency * x + start_place) * volume
    return y


def modulation(args, bits):
    """
    描述：FSK调制算法
    参数：全局参数, 0-1比特信号（规定比特信号长度小于等于一个包的限制）
    返回：得到的波---numpy格式的一维数组
    """
    result_wave = np.empty(shape=(1, 0))
    for bit in bits:
        if bit == 0:
            frequency = args.frequency_0
        else:
            frequency = args.frequency_1
        y = generate_pulse(args.framerate, frequency, args.volume, args.start_place, args.window_length)
        result_wave = np.append(result_wave, y)
    return result_wave

<<<<<<< HEAD
def get_correlates(args, wave):
    '''
    参数：全局参数，波
    描述：计算波和前导码的相关性
    返回：相关性
    '''
=======

def get_window_start(args, wave):
    """
    描述：用前导码对齐窗口
    参数：全局参数，波---numpy格式的一维数组
    返回：前导码在哪？
    """
>>>>>>> 6b09c8251c93b1d339966a9ae630b04320ccc69d
    preamble_seq = modulation(args, args.preamble)
    length = len(wave)
    length_preamble = len(preamble_seq)
    start = 0
    correlates = []
    while start + length_preamble <= length:
        the_wave = wave[start: start + length_preamble]
        correlate = np.dot(the_wave, preamble_seq)
<<<<<<< HEAD
        correlates.append(correlate)
        start += 1
    if args.test:
        plt.plot(correlates)
        plt.show()
    return correlates

def get_window_start(args, start, correlates):
    '''
    描述：用前导码对齐窗口
    参数：全局参数，开始位置，和前导码的相关系数
    返回：前导码在哪？
    '''
    real_wave_start_place = -1
    length_one = round(args.framerate * args.window_length)
    length_preamble = len(args.preamble) * length_one
    for i in range(len(correlates) - start):
        if(abs(correlates[i + start]) >= args.threshold and real_wave_start_place == -1):
            real_wave_start_place = i + start
            break
    if real_wave_start_place == -1:
        return -1

=======
        if abs(correlate) >= args.threshold and real_wave_start_place == -1:
            real_wave_start_place = start
        correlates.append(correlate)
        start += 1
    plt.plot(correlates)
    plt.show()
>>>>>>> 6b09c8251c93b1d339966a9ae630b04320ccc69d
    place = real_wave_start_place + np.argmax(correlates[real_wave_start_place:real_wave_start_place + length_preamble])

    if args.test:
        print(real_wave_start_place)
        print(correlates[real_wave_start_place:real_wave_start_place + length_preamble])
        print(place)
    return place


def demodulate_one(args, wave):
    """
    描述：获取主导频率来解码一个bit
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特
    """
    fourier_result = np.abs(np.fft.fft(wave))
    length = len(fourier_result)
    fourier_result = fourier_result[0: length // 2]
    freq0_place = int(args.frequency_0 * length / args.framerate)
    freq1_place = int(args.frequency_1 * length / args.framerate)
    freq0_v = np.max(fourier_result[freq0_place - 10:freq0_place + 10])
    freq1_v = np.max(fourier_result[freq1_place - 10:freq1_place + 10])
    return 0 if freq0_v > freq1_v else 1


<<<<<<< HEAD
def demodulate_packet(args, wave):
    '''
    描述：FSK解调一个包
=======
def demodulation(args, wave):
    """
    描述：FSK解调算法
>>>>>>> 6b09c8251c93b1d339966a9ae630b04320ccc69d
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特信号
    """
    # 绘制短时傅里叶变换图
    # f, t, zxx = signal.stft(wave, args.framerate)
    # plt.pcolormesh(t, f, np.abs(zxx))
    # plt.colorbar()
    # plt.title('STFT Magnitude')
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')
    # plt.tight_layout()
    length_one = round(args.framerate * args.window_length)
    length = len(wave)
    start = 0
    result = []
    while start + length_one <= length:
        sub_wave = wave[start: start + length_one]
        the_bit = demodulate_one(args, sub_wave)
        result.append(the_bit)
        start += length_one
    # plt.scatter(np.arange(0, len(result), 1) * 0.01 + 0.005, np.array(result) * 2500 + 7500, marker='o', c='r')
    # plt.scatter(np.arange(0, len(original_seq), 1) * 0.01 + 0.005, np.array(original_seq) * 2500 + 7600, marker='o', c='b')
    # plt.show()
    return result

<<<<<<< HEAD
def demodulation(args, wave):
    '''
    描述：FSK解调算法
    参数：全局参数，波
    返回：各个包的0-1参数
    '''
    length_one = round(args.framerate * args.window_length)
    correlates = get_correlates(args, wave)
    start = 0
    packet_results = []
    while True:
        #找起始位置
        start_place = get_window_start(args, start, correlates)
        print(start_place)
        if start_place < 0:
            break
        #之后28个bit---前导码20bit，8bit长度
        preamble_end = start_place + length_one * len(args.preamble)
        length_end = preamble_end + length_one * args.packet_head_length 
        preamble_wave = wave[start_place : preamble_end]
        length_wave = wave[preamble_end : length_end]

        #解码长度
        length_result = demodulate_packet(args, length_wave)
        length = bit_to_int(length_result)
        if length < 0:
            break

        #截取对应长度数据，解码
        packet_end = length_end + length_one * length
        packet_wave = wave[length_end:packet_end]
        packet_result = demodulate_packet(args, packet_wave)
        packet_results.append(packet_result)

        #更新位置
        start = packet_end
    return packet_results

if __name__ == '__main__':
    args = init_args()
    original_seq = get_original_seq(args)
    get_wave = load_wave(save_base = args.save_base_receive, file_name = 'res.wav')
    get_seq = demodulation(args, get_wave)
    accuracy_list = []
    for i in range(len(original_seq)):
        accuracy = get_accuracy(original_seq[i], get_seq[i])
        accuracy_list.append(accuracy)
        print("Data {}, Accuracy {:.4f}%".format(i + 1, accuracy * 100))
=======

def main():
    args = init_args()
    original_info = '北美奴隶种族灭绝反人类匪帮，必须被毁灭，入关！'
    original_seq = string_encode(original_info)

    # TODO:完整的蓝牙包，分包机制
    original_seq = np.append(args.preamble, original_seq)

    # get_wave = load_wave(save_base = args.save_base_send, file_name = 'kebab.wav')
    get_wave = load_wave(save_base=args.save_base_receive, file_name='o5.wav')
    get_wave = np.array([float(i[0]) for i in get_wave])

    print("??")
    print(len(get_wave))
    plt.plot(get_wave)
    plt.show()
    place = get_window_start(args, get_wave)
    get_seq = demodulation(args, get_wave[place:])

    # 临时代码，到时候应该用蓝牙包解码
    get_seq = get_seq[: len(original_seq)]

    err_count = 0
    for i in range(len(original_seq)):
        if get_seq[i] != original_seq[i]:
            err_count += 1

    # 错误率
    error = err_count / len(original_seq)
    print("{:.4f}%".format(error * 100))

    # TODO：用蓝牙包结构解码
    packet, place = decode_bluetooth_packet(args, get_seq)
    result = string_decode(packet)
    print(original_info)
    print(result)


if __name__ == '__main__':
    main()
>>>>>>> 6b09c8251c93b1d339966a9ae630b04320ccc69d
