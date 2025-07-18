# import settings
import math
import numpy as np
from pluto_interface import pluto_receiver
from matplotlib import pyplot

# Receiver parameters configuration
""" Parameters for PlutoSDR device """
rx_args = "ip:192.168.3.1"
rx_freq = 915e6
bandwidth = 1e6
rx_gain = 0

rx_buffer_size = 1e5
gain_control_mode = "fast_attack"
# gain_control_mode = "manual"
sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size, gain_control_mode, verbose=True).pluto

if __name__ == '__main__':
    # Receive the signal and record
    received_signal = sdr_rx.rx()  # Record a buffer size signal one time
    np.save("received_signal.npy", received_signal)
