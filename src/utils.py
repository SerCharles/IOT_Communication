import argparse


def init_args():
    '''
    描述：加载全局设置---窗口长度，0和1对应的频率，采样频率振幅等其他参数
    参数：无
    返回：args变量，对应全局设置
    '''
    parser = argparse.ArgumentParser(description="Choose the parameters")

    #0和1的频率
    parser.add_argument("--frequency_0", type = int, default = 10000)
    parser.add_argument("--frequency_1", type = int, default = 20000)

    #采样频率，振幅，宽度等通用设置
    parser.add_argument("--framerate", type = int, default = 48000)
    parser.add_argument("--sample_width", type = int, default = 2)
    parser.add_argument("--nchannels", type = int, default = 1)
    parser.add_argument("--volume", type = float, default = 10000.0)
    parser.add_argument("--start_place", type = int, default = 0)

    #单个窗口的长度(单位秒)
    parser.add_argument("--window_length", type = float, default = 0.01)

    #一个包最长长度(多少个比特)
    parser.add_argument("--packet_length", type = float, default = 1000)

    #保存和接收的文件夹名称
    parser.add_argument("--save_base_send", type = str, default = 'send')
    parser.add_argument("--save_base_receive", type = str, default = 'receive')
    args = parser.parse_args()
    return args