# ofdm_rx_main.py
from ofdm.pluto_interface import pluto_receiver
import numpy as np
import matplotlib.pyplot as plt

# PlutoSDR RX配置
rx_args = "ip:192.168.3.1"
rx_freq = 915e6
bandwidth = 1e6
rx_gain = 0
rx_buffer_size = int(2e5)
gain_control_mode = "fast_attack"

# 初始化接收器
sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size,
                        gain_control_mode, verbose=True).pluto

# 接收一次缓冲区信号
received_signal = sdr_rx.rx()
np.save("received_signal.npy", received_signal)
print("信号采集完成，已保存为 recorded_signal.npy")

# 可视化波形
plt.figure(figsize=(10,3))
plt.plot(np.real(received_signal), label='Real')
plt.plot(np.imag(received_signal), label='Imag', alpha=0.7)
plt.grid(True)
plt.title("Received Signal Waveform")
plt.legend()
plt.tight_layout()
plt.show()
