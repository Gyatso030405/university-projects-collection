import numpy as np
import matplotlib.pyplot as plt

# 参数
FFT_LEN = 64
CP_LEN = 16
NUM_DATA_CARRIERS = 48

# 子载波索引（对应48个数据子载波）
data_indices = np.array(
    list(range(1, 7)) +
    list(range(8, 21)) +
    list(range(22, 27)) +
    list(range(-26, -21)) +
    list(range(-20, -7)) +
    list(range(-6, 0))
)

# 载入信号和原始比特
rx_signal = np.load('received_signal.npy')
original_bits = np.load('raw_data.npy')

# 帧同步（简单搜索LTS）
def frame_sync_lts(signal):
    STS_LEN = 160  # 短训练序列长度
    LT_LEN = 160   # 长训练序列长度
    search_range = 3000  # 搜索区间可根据情况调整

    max_corr = 0
    start_index = 0
    for i in range(search_range):
        lts1 = signal[i + STS_LEN + 32 : i + STS_LEN + 96]
        lts2 = signal[i + STS_LEN + 96 : i + STS_LEN + 160]
        corr = np.abs(np.sum(np.conj(lts1) * lts2))
        if corr > max_corr:
            max_corr = corr
            start_index = i
    return start_index

start = frame_sync_lts(rx_signal)
print("Frame start at:", start)

# CFO估计（基于LTS）
def estimate_cfo(signal, start):
    STS_LEN = 160
    lts1 = signal[start + STS_LEN + 32 : start + STS_LEN + 96]
    lts2 = signal[start + STS_LEN + 96 : start + STS_LEN + 160]
    angle = np.angle(np.sum(np.conj(lts1) * lts2))
    cfo_est = angle / 64 / (1/(1e6))  # 简单示意，1e6是采样率
    return cfo_est

cfo = estimate_cfo(rx_signal, start)
print(f"Estimated CFO (rad/sample): {cfo}")

# CFO补偿
def correct_cfo(signal, cfo):
    n = np.arange(len(signal))
    corrected = signal * np.exp(-1j * cfo * n)
    return corrected

rx_corrected = correct_cfo(rx_signal, cfo)

# 信道估计（使用LTS）
def estimate_channel(signal, start):
    STS_LEN = 160
    lts1 = signal[start + STS_LEN + 32 : start + STS_LEN + 96]
    lts2 = signal[start + STS_LEN + 96 : start + STS_LEN + 160]
    lts_freq1 = np.fft.fftshift(np.fft.fft(lts1, FFT_LEN))
    lts_freq2 = np.fft.fftshift(np.fft.fft(lts2, FFT_LEN))
    channel_est = (lts_freq1 + lts_freq2) / 2
    return channel_est

channel_est = estimate_channel(rx_corrected, start)

# 提取payload
payload_start = start + 160 + 160
payload = rx_corrected[payload_start:]

# 解调
num_symbols = len(original_bits) // NUM_DATA_CARRIERS
demod_bits = []

for i in range(num_symbols):
    start_i = i * (CP_LEN + FFT_LEN)
    if start_i + CP_LEN + FFT_LEN > len(payload):
        break
    symbol = payload[start_i + CP_LEN : start_i + CP_LEN + FFT_LEN]
    freq = np.fft.fftshift(np.fft.fft(symbol))
    equalized = freq / channel_est
    data_subcarriers = equalized[data_indices + FFT_LEN // 2]
    # 简单判决
    bits = (np.real(data_subcarriers) > 0).astype(int)
    demod_bits.extend(bits)

demod_bits = np.array(demod_bits[:len(original_bits)])

# 计算准确率
num_correct = np.sum(demod_bits == original_bits)
accuracy = 100 * num_correct / len(original_bits)
print(f"解调完成！总比特数: {len(original_bits)}, 正确数: {num_correct}, 准确率: {accuracy:.2f}%")

# 输出前20比特
print("解调前20比特:", demod_bits[:20])
print("原始前20比特:", original_bits[:20])

# 估计SNR（星座图法）
signal_power = np.mean(np.abs(np.mean(data_subcarriers))**2)
noise_power = np.mean(np.abs(data_subcarriers - np.mean(data_subcarriers))**2)
snr = 10 * np.log10(signal_power / noise_power)
print(f"估计SNR: {snr:.2f} dB")

# 画星座图
plt.figure(figsize=(6,6))
plt.scatter(np.real(data_subcarriers), np.imag(data_subcarriers), color='blue', s=10)
plt.title("Equalized Data Subcarriers Constellation")
plt.xlabel("Real")
plt.ylabel("Imag")
plt.grid(True)
plt.axis('equal')
plt.show()
