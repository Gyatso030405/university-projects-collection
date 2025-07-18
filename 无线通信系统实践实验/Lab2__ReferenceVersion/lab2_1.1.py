import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from scipy.fftpack import fft
import math
'''
 preamble_lts：数据包长的前导码的两次重复序列
 '''
def channel_estimation(preamble_lts, index, lts_frequency):
    preamble_lts_1 = preamble_lts[0:64]
    preamble_lts_2 = preamble_lts[64:128]
    preamble_lts_avg = (preamble_lts_1 + preamble_lts_2) / 2
    preamble_lts_avg_f = np.fft.fft(preamble_lts_avg, 64)
    h = np.zeros(64,dtype=complex)
    for i in range(0,len(index)):
        h[index[i]] = np.divide(preamble_lts_avg_f[index[i]],lts_frequency[index[i]])
    return h 

'''
function: bpsk解调解调函数
params: rx_samples_data：已经完成帧同步，取出相应数据包的数据序列；
return: 有承载信息量的子载波解调得到的二进制序列
'''
def bpsk_demodulation(rx_samples_data, h_tilde, sym_num, data_index):
    demod = np.zeros(48 * 20)
    for symi in range(0,sym_num):
        #TODO: add phase tracking for real signal from SDR
       rx_data_samples_time = rx_samples_data[(symi) * 80 + 16 : (symi+1) * 80 - 1]
       rx_data_samples_freq = np.fft.fft(rx_data_samples_time, 64)
       h_temp = h_tilde
       for subi in range(0,len(data_index)):
           dis0 = abs(-h_temp[data_index[subi]-1] - rx_data_samples_freq[data_index[subi]-1])
           dis1 = abs(h_temp[data_index[subi]-1] - rx_data_samples_freq[data_index[subi]-1])
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
    preamble_sqrt = np.sqrt(np.sum(abs((preamble)**2)))
    for i in range(0,(signal_length - preamble_length-1)):
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
    return start_index, m


index1 = [i for i in range(2,8)] 
index2 = [i for i in range(9,22)] 
index3 = [i for i in range(23,28)] 
index4 = [i for i in range(39,44)] 
index5 = [i for i in range(45,58)] 
index6 = [i for i in range(59,65)] 
data_index=np.hstack((index1,index2,index3,index4,index5,index6))
index = [i for i in range(0,64)]
preamble_lts = np.load("preamble_lts.npy")
preamble_sts = np.transpose(np.load("preamble_sts.npy"))
raw_data = np.transpose(np.load("raw_data.npy"))
tx_signal = np.transpose(np.load("tx_signal.npy"))
lts_frequency = np.fft.fft(preamble_lts, 64) 
'''N:子载波的数量，即进行ifft的长度；cp_len：循环前缀长度； pilot_index：导频的下标； 
            lts_preamble：前导码序列'''
if __name__ == '__main__':
    [start_index,m] = detect_preamble_cross_correlation(preamble_lts,tx_signal)
    #start_index = detect_preamble_by_sliding_window(tx_signal,16)
    '''N:子载波的数量，即进行ifft的长度；cp_len：循环前缀长度； pilot_index：导频的下标； 
                lts_preamble：前导码序列,symbol_num:符号数'''
    290+680+1300
    cp_cut = -8
    start_pos = start_index[0] + cp_cut 
    symbol_num = 20  
    rx_samples = tx_signal[start_pos:start_pos+64*2+symbol_num*80]
    rx_samples_lts = rx_samples[0:128]
    rx_samples_data = rx_samples[128:]
    h_tilde = channel_estimation(rx_samples_lts,index,lts_frequency)
  
    demod_signal = bpsk_demodulation(rx_samples_data, h_tilde, symbol_num, data_index)
    nbits = symbol_num * 48
    snr = math.inf 
    num_error = 0
    for i in range(0,nbits):
        if(demod_signal[i] != raw_data[i]):
            num_error += 1
            print(i)
    print("snr = %f num_error = %d, BER = %f \n" % (snr, num_error, num_error/nbits))

   # -21 -7 7 21