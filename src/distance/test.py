# -*- coding: utf-8 -*-
import FSK
import utils


def main():
    packets = FSK.demodulation(utils.init_args(), utils.load_wave("", "_tmp_a_0_6535.wav"))

if __name__ == '__main__':
    main()
