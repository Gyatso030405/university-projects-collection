import matplotlib.pyplot as plt
import numpy as np
import scipy.io  # 原来写错为1o，修正

from pluto_interface import pluto_receiver

# 定义前导码检测函数：互相关检测
def detect_preamble_cross_correlation(preamble, signal):
    correlation = []
    L = len(preamble)
    for n in range(len(signal) - 2 * L + 1):
        A = preamble[0:L]
        B = signal[n:n + L]
        correlation.append(abs(np.sum(B.conj() * A)))
    return correlation

""" Parameters for PlutoSDR device """
rx_args = "ip:192.168.3.1"
rx_freq = 915e6
bandwidth = 1e6
rx_gain = 40  # 补上缺失的接收增益
rx_buffer_size = int(1e5)
gain_control_mode = "fast_attack"

# 初始化 Pluto 接收端
sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size, gain_control_mode, verbose=True).pluto

# 接收一段信号
received_signal = sdr_rx.rx()  # 一次性读取 buffer 大小的数据
np.save("recorded_signal.npy", received_signal)

# 画接收信号
plt.subplot(2, 1, 1)
x_received_signal = np.arange(1, len(received_signal) + 1)
plt.plot(x_received_signal, abs(received_signal), label='received_signal')
plt.title('Received Signal')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()

# 加载预定义前导码
preamble_lts = np.load("preamble_lts.npy")
preamble_sts = np.load("preamble_sts.npy")

# 选择更强的接收数据用于互相关检测
received_signal_strong = np.load("recorded_signal_strong.npy")

# 互相关检测
cross_correlation_signal = detect_preamble_cross_correlation(preamble_sts, received_signal_strong)
x_cross_correlation_signal = np.arange(1, len(cross_correlation_signal) + 1)

# 画互相关结果
plt.subplot(2, 1, 2)
plt.plot(x_cross_correlation_signal, abs(cross_correlation_signal), label='cross_correlation_signal')
plt.title('Cross Correlation Result')
plt.xlabel('Sample Index')
plt.ylabel('Correlation')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
