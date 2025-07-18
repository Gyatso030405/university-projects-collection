import numpy as np
import matplotlib.pyplot as plt

# 常量
FFT_LEN = 64
CP_LEN = 16
NUM_DATA_CARRIERS = 48
ST_LEN = 160  # 10 STS, 每个16采样
LT_LEN = 160  # 2.5 LTS

# 子载波索引（同 1.1）
data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)

# 加载信号和原始比特
rx_signal = np.load('recorded_signal_strong.npy')
original_bits = np.load('raw_data.npy')

# 帧同步(基于STS自相关)
def frame_sync_sts(signal, sts_len=16, threshold=0.8):
    corr = []
    for i in range(len(signal) - 2 * sts_len):
        s1 = signal[i:i+sts_len]
        s2 = signal[i+sts_len:i+2*sts_len]
        c = np.vdot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2) + 1e-6)
        corr.append(np.abs(c))
    corr = np.array(corr)
    peak_index = np.argmax(corr)
    return peak_index  # 起始位置为10个STS的开始

# CFO粗补偿
def estimate_cfo(signal, start):
    # 从10个STS中提取后两个周期做估计
    sts1 = signal[start + 8*16 : start + 9*16]
    sts2 = signal[start + 9*16 : start + 10*16]
    phase_diff = np.angle(np.vdot(sts1, sts2))
    cfo_est = phase_diff / (2 * np.pi * 16)
    return cfo_est

def correct_cfo(signal, cfo, Fs=20e6):
    n = np.arange(len(signal))
    return signal * np.exp(-1j * 2 * np.pi * cfo * n)

# 提取LTS，估计信道
# 找到起点
start = frame_sync_sts(rx_signal)
print("Frame start at:", start) #整个 recorded_signal_strong.npy 中，数据包是从第XX个采样点开始的。

# CFO估计与校正
cfo = estimate_cfo(rx_signal, start)
print("Estimated CFO:", cfo)  #载波频偏
rx_corrected = correct_cfo(rx_signal, cfo)

# LTS频域平均估计
lts_start = start + ST_LEN
lts1 = rx_corrected[lts_start + 32 : lts_start + 96]
lts2 = rx_corrected[lts_start + 96 : lts_start + 160]
# LTS 总长度是 160（32 CP + 64 + 64）
#lts_start = start + ST_LEN + 32
#lts = rx_corrected[lts_start : lts_start + 64]
#lts_freq = np.fft.fftshift(np.fft.fft(lts, FFT_LEN))
#channel_est = lts_freq  # 用一个 LTS 就够了

lts1_freq = np.fft.fftshift(np.fft.fft(lts1, FFT_LEN))
lts2_freq = np.fft.fftshift(np.fft.fft(lts2, FFT_LEN))
channel_est = (lts1_freq + lts2_freq) / 2

# 解调每个符号（FFT + 均衡 + 判决）
# 提取数据区
payload_start = lts_start + LT_LEN
payload = rx_corrected[payload_start:]


# 符号数估计
num_symbols = int(np.ceil(len(original_bits) / NUM_DATA_CARRIERS))
demod_bits = []

for i in range(num_symbols):
    start_i = i * (CP_LEN + FFT_LEN)
    if start_i + CP_LEN + FFT_LEN > len(payload):
        break
    symbol = payload[start_i + CP_LEN : start_i + CP_LEN + FFT_LEN]
    freq = np.fft.fftshift(np.fft.fft(symbol))
    equalized = freq / channel_est
    data_subcarriers = equalized[data_indices + FFT_LEN//2]
    # 简单纠正整体相位偏移
    if np.mean(np.real(data_subcarriers)) < 0:
        data_subcarriers *= -1
    bits = (np.real(data_subcarriers) > 0).astype(int)
    demod_bits.extend(bits)

demod_bits = np.array(demod_bits[:len(original_bits)])

# shuchuzhunquelv
num_correct = np.sum(demod_bits == original_bits)
accuracy = 100 * num_correct / len(original_bits)
print(f"解调完成！总比特数: {len(original_bits)}, 正确数: {num_correct}, 准确率: {accuracy:.2f}%")
