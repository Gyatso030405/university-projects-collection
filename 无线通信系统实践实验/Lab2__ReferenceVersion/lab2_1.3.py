import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from scipy.fftpack import fft
from scipy.fft import fftshift
import math
from scipy import optimize



def channel_estimation(preamble_lts, index, lts_frequency): 

    preamble_lts_1 = preamble_lts[0:64]
    preamble_lts_2 = preamble_lts[64:128]
    preamble_lts_avg = (preamble_lts_1 + preamble_lts_2) / 2
    preamble_lts_avg_f = np.fft.fft(preamble_lts_avg, 64)
    h = np.zeros(64,dtype=complex)
    for i in range(0,len(index)):
        h[index[i]] = np.divide(preamble_lts_avg_f[index[i]],lts_frequency[index[i]])
    return h 


def bpsk_demodulation( h_tilde, sym_num, data_index,signal,pilot_index):
    demod = np.zeros(48 * sym_num)
    for symi in range(0,sym_num):
        #TODO: add phase tracking for real signal from SDR
        h_temp = h_tilde
        signal_time = signal[symi*80 + 16: (symi + 1) * 80]
        signal_freq = np.fft.fft(signal_time)
        pilot_temp = signal_freq[pilot_index] / h_temp[pilot_index]
        pilot_temp = fftshift(pilot_temp)
        compensate = phase_track(pilot_temp,pilot_value,pilot_index)
        signal_freq = signal_freq * compensate
        for subi in range(len(data_index)):
           dis0 = abs(-h_temp[data_index[subi]-1] - signal_freq[data_index[subi]-1])
           dis1 = abs(h_temp[data_index[subi]-1] - signal_freq[data_index[subi]-1])
           if dis0 > dis1:
               demod[subi + (symi) * len(data_index)] = 1
           else:
               demod[subi + (symi) * len(data_index)] = 0
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



def cfo_estimation(rx_samples_lts):
    preamble_lts_1 = rx_samples_lts[0:64]
    preamble_lts_2 = rx_samples_lts[64:128]
    lts_corr = (np.sum(np.dot(preamble_lts_1.conj(),preamble_lts_2)))
    cfo_comp = np.angle(lts_corr) / (2 *math.pi) / 64
    return cfo_comp

def f_1(x, A, B):
    return A * x + B

def phase_track(pilot_signal_freq,pilot_value,pilot_index):
    pilot_angle = np.angle(pilot_value / pilot_signal_freq)

    A1, B1 = optimize.curve_fit(f_1, pilot_index, pilot_angle)[0]
    compensate = np.exp(np.arange(-32, 32) * A1)
    return np.concatenate((compensate[32:], compensate[0:32]), axis=0)

index1 = [i for i in range(2,8)] 
index2 = [i for i in range(9,22)] 
index3 = [i for i in range(23,28)] 
index4 = [i for i in range(39,44)] 
index5 = [i for i in range(45,58)] 
index6 = [i for i in range(59,65)] 
data_index = np.hstack((index1,index2,index3,index4,index5,index6))
index = [i for i in range(0,64)]
preamble_lts = np.load('preamble_lts.npy')  
preamble_sts = np.load("preamble_sts.npy")
tx_signal = np.load("recorded_signal_100sym.npy")
#tx_signal = np.load("recorded_signal_10sym.npy")
raw_data = np.load("raw_data.npy")
lts_frequency = fft(preamble_lts, 64) 
snr = math.inf



if __name__ == '__main__':
    [start_index,_] = detect_preamble_cross_correlation(preamble_lts,tx_signal)
    N = 64
    cp_cut = -8
    start_index  += cp_cut
    cp_len = 16
    symbol_num = 100
    #symbol_num = 10  
    signal = tx_signal[start_index[0]:start_index[0]+64*2+symbol_num*80]
    signal_lts_raw = signal[0:128]
    pilot_index=[7, 21, 43, 57]
    pilot_value=[1,-1,1,1]

    # % cfo estimation
    cfo = cfo_estimation(signal_lts_raw)

    #% cfo compensation
    for i in range(0, 128 + symbol_num * ( N  + cp_len)):
        signal[i] = signal[i] * np.exp( -1j * 2 * math.pi * cfo * i)

    #% channel estimation by preamble
    h_tilde = channel_estimation(signal_lts_raw,index,lts_frequency)

    signal_data = signal[128 : 128 + symbol_num * ( N + cp_len)]
    demod_signal = bpsk_demodulation( h_tilde, symbol_num, data_index,signal_data,pilot_index)
    np.save('data_100',demod_signal)
    #np.save('data_10',demod_signal)