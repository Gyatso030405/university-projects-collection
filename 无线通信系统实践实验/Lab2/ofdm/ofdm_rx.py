import numpy as np
from ofdm.pluto_interface import pluto_receiver
from ofdm.ofdm_utils import OfdmConfig
from scipy.signal import correlate
import matplotlib.pyplot as plt


class OfdmRx:
    def __init__(self, rx_args, rx_freq, bandwidth, rx_gain, buffer_size,
                 n=64, cp_len=16, qam_mod_size=2, pilot_pattern='custom', preamble_type='802.11',
                 gain_control_mode='slow_attack', verbose=False):
        self.rx_args = rx_args
        self.rx_freq = rx_freq
        self.bandwidth = bandwidth
        self.rx_gain = rx_gain
        self.buffer_size = int(buffer_size)
        self.verbose = verbose

        self.sdr = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain,
                                  buffer_size, gain_control_mode, verbose=verbose).pluto
        self.config = OfdmConfig(n, cp_len, qam_mod_size, pilot_pattern)
        self.n = n
        self.cp_len = cp_len

    def receive(self):
        rx_signal = self.sdr.rx()
        return rx_signal

    def frame_sync(self, rx_signal):
        sts = self.config.preamble[0:16 * 10]  # 160 sample STS
        corr = np.abs(correlate(rx_signal, sts, mode='valid'))
        start = np.argmax(corr)
        return start

    def estimate_cfo(self, lts_cp):
        # Estimate CFO using the two LTS symbols
        lts1 = lts_cp[32:96]
        lts2 = lts_cp[96:160]
        cfo_angle = np.angle(np.vdot(lts1, lts2))
        cfo_est = cfo_angle / (64)
        return cfo_est

    def correct_cfo(self, rx_signal, cfo_est):
        time_idx = np.arange(len(rx_signal))
        return rx_signal * np.exp(-1j * cfo_est * time_idx)

    def demodulate(self, rx_signal, num_symbols=100):
        start = self.frame_sync(rx_signal)
        if self.verbose:
            print("Frame starts at:", start)

        lts_cp = rx_signal[start + 160:start + 320]
        cfo_est = self.estimate_cfo(lts_cp)
        rx_signal = self.correct_cfo(rx_signal, cfo_est)

        lts1 = rx_signal[start + 192:start + 256]
        lts2 = rx_signal[start + 256:start + 320]
        lts_freq = np.fft.fftshift(np.fft.fft(lts1))
        channel_est = lts_freq

        payload_start = start + 320
        payload = rx_signal[payload_start:]

        symbols = []
        for i in range(num_symbols):
            sym_start = i * (self.n + self.cp_len)
            if sym_start + self.n + self.cp_len > len(payload):
                break
            symbol = payload[sym_start + self.cp_len: sym_start + self.cp_len + self.n]
            freq = np.fft.fftshift(np.fft.fft(symbol))
            equalized = freq / channel_est
            symbols.append(equalized)

        all_symbols = np.stack(symbols, axis=1)

        # Pilot tracking
        pilots_idx, data_idx = self.config.ofdm_pilot.get_index_array_at_symbol(np.array([0]))
        pilots_idx = pilots_idx[0]
        data_idx = data_idx[0]

        demod_bits = []

        for i in range(all_symbols.shape[1]):
            symbol = all_symbols[:, i]
            pilot_phase = np.angle(symbol[pilots_idx])
            mean_phase = np.mean(pilot_phase)
            symbol *= np.exp(-1j * mean_phase)

            data = symbol[data_idx]
            bits = (np.real(data) > 0).astype(int)
            demod_bits.extend(bits)

        return np.array(demod_bits)

    def visualize_constellation(self, symbols, data_idx):
        data_symbols = symbols[data_idx, :].flatten()
        plt.figure()
        plt.scatter(np.real(data_symbols), np.imag(data_symbols), s=5)
        plt.title("Equalized Constellation (Data Subcarriers)")
        plt.grid(True)
        plt.xlabel("Real")
        plt.ylabel("Imag")
        plt.axis('equal')
        plt.show()
