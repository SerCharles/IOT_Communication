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
    code0 = generate_pulse(args.framerate, args.frequency_0, args.volume, args.start_place, args.window_length)
    code1 = generate_pulse(args.framerate, args.frequency_1, args.volume, args.start_place, args.window_length)
    code2 = generate_pulse(args.framerate, 1, 0, args.start_place, args.window_length)
    code_len = len(code0)
    result_wave = np.zeros(shape=(code_len * len(bits)))
    start_index = 0
    for bit in bits:
        if bit == 2:  # for blank
            result_wave[start_index: start_index + code_len] = code2
        else:
            if bit == 0:
                result_wave[start_index: start_index + code_len] = code0
            else:
                result_wave[start_index: start_index + code_len] = code1
        start_index += code_len
    return result_wave


def get_correlates(args, wave):
    '''
    参数：全局参数，波
    描述：计算波和前导码的相关性
    返回：相关性
    '''
    preamble_seq = modulation(args, args.preamble)
    length = len(wave)
    length_preamble = len(preamble_seq)
    start = 0
    correlates = []
    while start + length_preamble <= length:
        the_wave = wave[start: start + length_preamble]
        correlate = np.dot(the_wave, preamble_seq)
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
        if abs(correlates[i + start]) >= args.threshold and real_wave_start_place == -1:
            real_wave_start_place = i + start
            break
    if real_wave_start_place == -1:
        return -1

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
    max_place = np.argmax(fourier_result)
    max_freq = round(max_place / length * args.framerate)
    dist_0 = abs(max_freq - args.frequency_0)
    dist_1 = abs(max_freq - args.frequency_1)
    if dist_0 < dist_1:
        return 0
    else:
        return 1


def demodulate_packet(args, wave):
    '''
    描述：FSK解调一个包
    参数：全局参数，波---numpy格式的一维数组
    返回：0-1比特信号
    '''
    length_one = round(args.framerate * args.window_length)
    length = len(wave)
    start = 0
    result = []
    while start + length_one <= length:
        sub_wave = wave[start: start + length_one]
        the_bit = demodulate_one(args, sub_wave)
        result.append(the_bit)
        start += length_one
    return result


def demodulation(args, wave):
    """
    描述：FSK解调算法
    参数：全局参数，波
    返回：各个包的0-1参数
    """
    length_one = round(args.framerate * args.window_length)
    correlates = get_correlates(args, wave)
    start = 0
    packet_results = []
    while start < len(wave):
        # 找起始位置
        start_place = get_window_start(args, start, correlates)
        print(start_place)
        if args.beep_beep and (1.5 * args.framerate <= start_place <= 2.3 * args.framerate):
            start += int(0.2 * args.framerate)
            continue
        if start_place < 0:
            break
        # 之后28个bit---前导码20bit，8bit长度
        preamble_end = start_place + length_one * len(args.preamble)
        length_end = preamble_end + length_one * args.packet_head_length
        preamble_wave = wave[start_place: preamble_end]
        length_wave = wave[preamble_end: length_end]

        # 解码长度
        length_result = demodulate_packet(args, length_wave)
        length = bit_to_int(length_result)
        if args.beep_beep:
            length = 0
        if length < 0:
            break

        # 截取对应长度数据，解码
        packet_end = length_end + length_one * length
        packet_wave = wave[length_end:packet_end]
        packet_result = demodulate_packet(args, packet_wave)
        packet_results.append((packet_result, start_place))

        # 更新位置
        start = packet_end
    return packet_results


def test_fsk():
    '''
    描述：根据助教要求测试FSK
    参数：无
    返回：无
    '''
    args = init_args()
    original_seq = get_original_seq(args)
    get_wave = load_wave(save_base=args.save_base_receive, file_name='res.wav')
    get_seq = demodulation(args, get_wave)
    accuracy_list = []
    result_list = []
    for i in range(len(original_seq)):
        seq, off = get_seq[i]
        result_list.append(seq)
        accuracy = get_accuracy(original_seq[i], seq)
        accuracy_list.append(accuracy)
        print("Data {}, Accuracy {:.4f}%".format(i + 1, accuracy * 100))
    output_decoded_seq(args, result_list)


if __name__ == '__main__':
    test_fsk()
    # args = init_args()
    # original_seq = get_original_seq(args)
    # get_wave = load_wave(save_base=args.save_base_receive, file_name='res.wav')
    # get_seq = demodulation(args, get_wave)
    # csvfile = open("result.csv", "w", newline="")
    # writer = csv.writer(csvfile)
    # for seq_tup in get_seq:
    #     writer.writerow([len(seq_tup[0])] + seq_tup[0])
    # csvfile.close()
