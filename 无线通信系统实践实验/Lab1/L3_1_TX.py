import matplotlib.pyplot as plt
import numpy as np
import time

# Transmitter parameters configuration
from pluto_interface import pluto_transmitter

""" Parameters for PlutoSDR device """
tx_args = "ip:192.168.3.1"
tx_freq = 915e6
bandwidth = 1e6
tx_gain = -60

# 初始化发送端
sdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto

# 获取要发送的信号
transmitted_signal = np.load("tx_signal.npy")
transmitted_signal = transmitted_signal * (2 ** 14)

# 循环发送信号
for ii in range(10000):
    sdr_tx.tx(transmitted_signal)  # Cyclic transmit the signal
    time.sleep(0.01)
    print(ii)

# 可视化发送的信号
x_transmitted_signal = np.arange(1, len(transmitted_signal) + 1)
plt.plot(x_transmitted_signal, abs(transmitted_signal), label='transmitted_signal')
plt.xlabel('Sample Index')
plt.ylabel('Amplitude')
plt.title('Transmitted Signal')
plt.legend()
plt.grid(True)
plt.savefig("output.png")
plt.show()
