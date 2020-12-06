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


def get_window_start(args, wave):
    """
    描述：用前导码对齐窗口
    参数：全局参数，波---numpy格式的一维数组
    返回：前导码在哪？
    """
    preamble_seq = modulation(args, args.preamble)
    length = len(wave)
    length_preamble = len(preamble_seq)
    start = 0
    correlates = []
    real_wave_start_place = -1
    while start + length_preamble <= length:
        the_wave = wave[start: start + length_preamble]
        correlate = np.dot(the_wave, preamble_seq)
        if abs(correlate) >= args.threshold and real_wave_start_place == -1:
            real_wave_start_place = start
        correlates.append(correlate)
        start += 1
    plt.plot(correlates)
    plt.show()
    place = real_wave_start_place + np.argmax(correlates[real_wave_start_place:real_wave_start_place + length_preamble])
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


def demodulation(args, wave):
    """
    描述：FSK解调算法
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
