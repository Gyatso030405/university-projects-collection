from pluto_interface import pluto_receiver
import numpy as np
# PlutoSDR配置
rx_args = "ip:192.168.3.2"
rx_freq = 915e6
bandwidth = 1e6
rx_gain = 0
rx_buffer_size = 100000
gain_control_mode = "fast_attack"

# 接收信号
sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain,
                        rx_buffer_size, gain_control_mode).pluto
received_signal = sdr_rx.rx()

# 保存信号
np.save("recorded_signal.npy", received_signal)
print(f"Signal saved! Size: {received_signal.shape}, Type: {received_signal.dtype}")