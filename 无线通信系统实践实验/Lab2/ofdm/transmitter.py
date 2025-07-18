# import settings
import numpy as np
from pluto_interface import pluto_transmitter
from ofdm_tx import OfdmTx
import time

# Transmitter parameters configuration
""" Parameters for PlutoSDR device """
tx_args = "ip:192.168.2.1"
tx_freq = 915e6
bandwidth = 1e6
tx_gain = -20
sdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto


if __name__ == '__main__':
    # Parameters for OFDM PHY
    n = 64  # Number of bits within every OFDM symbol
    cp = 16  # length of cyclic prefix within every OFDM symbol
    qam_size = 2
    pilot_pattern = 'custom'
    preamble_type = '802.11'
    num_symbol = 100
    ofdm_transmitter = OfdmTx(tx_args, tx_freq, bandwidth, tx_gain, n, cp, qam_size, pilot_pattern , preamble_type, num_symbol, verbose=True)
    raw_data = np.random.randint(low=0, high=2, size=4800)
    np.save("lab2_raw_signal.npy", raw_data)
    OFDM_packet = ofdm_transmitter.process(raw_data) # Generate transmitted signal
    transmitted_signal = OFDM_packet * (2 ** 14)
    sdr_tx.tx_cyclic_buffer = False
    for packet_num in range(0, 1000):
        sdr_tx.tx(transmitted_signal)
        # time.sleep(0.01)
        print("Tx num:", packet_num)
