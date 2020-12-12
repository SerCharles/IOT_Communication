# -*- coding: utf-8 -*-
import os
import random
import scipy.signal as signal
from typing import Dict, Union

from scipy.io import wavfile

import FSK


beep_index = 0


def find_beeps(args, raw_wave) -> (int, int):
    packets = FSK.demodulation(args, raw_wave)
    beep0, beep1 = -1, -1
    if len(packets) >= 1:
        beep0 = packets[0][1] / args.framerate
    if len(packets) >= 2:
        beep1 = packets[1][1] / args.framerate
    return beep0, beep1


def calculate_distance(args, bytes1, bytes2) -> Dict[str, Union[float, int]]:
    global beep_index
    temp1 = "_tmp_a_" + str(beep_index) + "_" + str(random.randint(0, 32768)) + ".wav"
    temp2 = "_tmp_b_" + str(beep_index) + "_" + str(random.randint(0, 32768)) + ".wav"
    beep_index += 1
    # b, a = signal.butter(8, [2 * (args.frequency_0 - 200) / args.framerate,
    #                          2 * (args.frequency_1 + 200) / args.framerate], "bandpass")
    with open(temp1, "wb") as f:
        f.write(bytes1)
    fs, wave1 = wavfile.read(temp1)
    # wave1 = signal.filtfilt(b, a, wave1)
    with open(temp2, "wb") as f:
        f.write(bytes2)
    fs, wave2 = wavfile.read(temp2)
    # wave2 = signal.filtfilt(b, a, wave2)
    try:
        os.remove(temp1)
        os.remove(temp2)
    except:
        pass
    # 假设 wave1 和 wave2 分别开始于 ta0, tb2
    ta1, ta3 = find_beeps(args, wave1)
    tb1, tb3 = find_beeps(args, wave2)
    if ta1 == -1 or tb1 == -1:
        return {
            "distance": -1,
            "ta1": float(ta1),
            "ta3": float(ta3),
            "tb1": float(tb1),
            "tb3": float(tb3)
        }
    # 声速
    c = args.sound_velocity
    # 姑且认为 daa 和 dbb 为 0
    daa = 0
    dbb = 0
    # daa = c * (ta1 - args.delay_a)
    # dbb = c * (tb1 - args.delay_b)
    d = c / 2 * ((ta3 - ta1) - (tb3 - tb1)) + daa + dbb
    return {
        "distance": float(d),
        "ta1": float(ta1),
        "ta3": float(ta3),
        "tb1": float(tb1),
        "tb3": float(tb3)
    }
