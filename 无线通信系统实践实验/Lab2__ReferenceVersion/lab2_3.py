# Transmitter parameters configuration  
import numpy as np
from pluto_interface import pluto_transmitter
from matplotlib import pyplot as plt
from pluto_interface import pluto_transmitter

from scipy.fftpack import fft
from scipy.fft import fftshift
import math
from scipy import optimize
import time


def channel_estimation(preamble_lts, index, lts_frequency):

    preamble_lts_1 = preamble_lts[0:64]
    preamble_lts_2 = preamble_lts[64:128]
    preamble_lts_avg = (preamble_lts_1 + preamble_lts_2) / 2
    preamble_lts_avg_f = np.fft.fft(preamble_lts_avg, 64)
    h = np.zeros(64,dtype=complex)
    for i in range(0,len(index)):
        h[index[i]] = np.divide(preamble_lts_avg_f[index[i]],lts_frequency[index[i]])
    return h


def bpsk_demodulation( h_tilde, sym_num, data_index,signal,pilot_index,pilot_value):
    demod = np.zeros(48 * sym_num)
    signal_data = []
    for symi in range(0,sym_num):
        #TODO: add phase tracking for real signal from SDR
        h_temp = h_tilde
        signal_time = signal[symi*80 + 16: (symi + 1) * 80]
        signal_freq = np.fft.fft(signal_time)
        pilot_temp = signal_freq[pilot_index] / h_temp[pilot_index]
        pilot_temp = fftshift(pilot_temp)
        compensate = phase_track(pilot_temp,pilot_value,fftshift(pilot_index))
        signal_freq = signal_freq * compensate
        signal_data.append(signal_freq/h_temp)
        for subi in range(len(data_index)):
          dis0 = abs(-h_temp[data_index[subi]-1] - signal_freq[data_index[subi]-1])
          dis1 = abs(h_temp[data_index[subi]-1] - signal_freq[data_index[subi]-1])
          if dis0 > dis1:
              demod[subi + (symi) * len(data_index)] = 1
          else:
              demod[subi + (symi) * len(data_index)] = 0
    plt.scatter(np.array(signal_data).real, np.array(signal_data).imag, marker='.')
    plt.title('planisphere')
    plt.show()
    return demod


def detect_preamble_cross_correlation(preamble, signal):
    preamble_length = len(preamble)
    signal_length = len(signal)
    correlation_threshold = 0.76
    m = []
    start_index = []
    lts_index = []
    preamble_sqrt = np.sqrt(np.sum(abs((preamble.conj() * preamble))))
    for i in range(1,(signal_length - preamble_length)):
        cn = abs(np.sum(preamble * signal[i:i+preamble_length].conj()))
        yn = abs(np.sqrt(np.sum(signal[i:i+preamble_length] * signal[i:i+preamble_length].conj())))
        pn = preamble_sqrt * yn
        if pn != 0:
            mn = cn / pn
        else:
            mn = 0
        m.append(mn)
        if mn > correlation_threshold:
                lts_index.append(i)
    pkt_number =int(np.fix(len(lts_index) / 2))
    for n  in range(1,pkt_number+1):
        start_index.append(lts_index[(n-1)*2])
    # plt.plot(m)
    # plt.show()
    return np.array(start_index), m


def detect_SNR(signal):
    power = 0
    c = np.zeros(len(signal))
    for n in range(len(signal)):
        c[n] = abs(signal[n]) ** 2
        power = c[n] + power
    aver = np.mean(c)
    threshold = 8 * aver
    index = []
    x = []
    flag = 1
    end_index = []
    for i in range(10, len(signal)):
        x = (np.sum(c[i - 100:i + 100]))
        if (x > threshold) & (flag == 1):
            index.append(i)
            flag = 0
        if (flag == 0) & (x < threshold):
            flag = 1
            end_index.append(i)
    # SNR
    SNR = []
    for i in range(len(index)-1):
        S = np.mean(c[:end_index[i]])
        N = np.mean(abs(c[end_index[i]:index[i + 1]]))
        SNR.append(10 * np.log2(1 + S / N))
    print('SNR = ', SNR, 'dB')
    return

def cfo_estimation(rx_samples_lts):
    preamble_lts_1 = rx_samples_lts[0:64]
    preamble_lts_2 = rx_samples_lts[64:128]
    lts_corr = (np.sum(np.dot(preamble_lts_1.conj(),preamble_lts_2)))
    cfo_comp = np.angle(lts_corr) / (2 *math.pi) / 64
    return cfo_comp

def f_1(x, A, B):
    return A * x + B

def phase_track(pilot_signal_freq,pilot_value,pilot_index):
    pilot_angle = np.angle( pilot_signal_freq/pilot_value)

    A1, B1 = optimize.curve_fit(f_1, pilot_index, pilot_angle)[0]
    compensate = np.exp(-1j*(B1+A1*np.arange(-32,32)))
    return compensate
if __name__ == '__main__':

    """ Parameters for PlutoSDR device """
    tx_args = "ip:192.168.2.1"
    tx_freq = 915e6
    bandwidth = 1e6
    tx_gain = 0
    sdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto
    # Get transmitted signal and transmit
    transmitted_signal = np.load("tx_signal.npy")
    transmitted_signal = transmitted_signal * (2 ** 14)
    plt.plot(transmitted_signal)
    plt.title("1")
    plt.show()
    sdr_tx.tx_cyclic_buffer = True
    sdr_tx.tx(transmitted_signal) # Cyclic transmit the signal

    # Receiver parameters configuration
    from pluto_interface import pluto_receiver
    """ Parameters for PlutoSDR device """
    rx_args = "ip:192.168.3.1"
    rx_freq = 915e6
    bandwidth = 1e6
    rx_gain = 10
    rx_buffer_size = 1e4
    gain_control_mode = "fast_attack"
    sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size, gain_control_mode, verbose=True).pluto
    # Receive the signal and record
    received_signal = sdr_rx.rx() # Record a buffer size signal one time
    plt.plot(received_signal)
    plt.title("received_signal")
    plt.show()
    #np.save("recorded_signal_test.npy", received_signal)

    index1 = [i for i in range(2, 8)]
    index2 = [i for i in range(9, 22)]
    index3 = [i for i in range(23, 28)]
    index4 = [i for i in range(39, 44)]
    index5 = [i for i in range(45, 58)]
    index6 = [i for i in range(59, 65)]
    data_index = np.hstack((index1, index2, index3, index4, index5, index6))
    index = [i for i in range(0, 64)]
    preamble_lts = np.load('preamble_lts.npy')
    preamble_sts = np.load("preamble_sts.npy")
    signal = received_signal
    SNR = detect_SNR(signal)
    raw_data = np.load("raw_data.npy")
    lts_frequency = fft(preamble_lts, 64)
    snr = math.inf
    [start_index, _] = detect_preamble_cross_correlation(preamble_lts, signal)
    print('start_index = ', start_index)
    N = 64
    cp_cut = -8
    start_index += cp_cut
    cp_len = 16
    symbol_num = 20
    # signal = tx_signal[start_index[0]:start_index[0]+64*2+symbol_num*80]
    pilot_index = [7, 21, 43, 57]
    pilot_value = [1, -1, 1, 1]

    # % cfo estimation
    signal_lts_raw = signal[start_index[0]:start_index[0] + 128]
    cfo = cfo_estimation(signal_lts_raw)

    # % cfo compensation
    for i in range(start_index[0], start_index[0] + 128 + symbol_num * 80):
        signal[i] = signal[i] * np.exp(-1j * 2 * np.pi * cfo * (i - 222))
    # % channel estimation by preamble
    signal_lts_new = signal[start_index[0]:start_index[0] + 128]
    h_tilde = channel_estimation(signal_lts_new, index, lts_frequency)

    signal_data = signal[start_index[0] + 128: start_index[0] + 128 + symbol_num * (N + cp_len)]
    demod_signal = bpsk_demodulation(h_tilde, symbol_num, data_index, signal_data, pilot_index, pilot_value)
    num_error = 0
    for i in range(0, 960):
        if (demod_signal[i] != raw_data[i]):
            num_error += 1
    print("snr = %f num_error = %d, BER = %f \n" % (snr, num_error, num_error / 960))


