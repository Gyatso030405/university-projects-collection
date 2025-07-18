import numpy as np
import matplotlib.pyplot as plt

# 参数设定
FFT_LEN = 64
CP_LEN = 16
NUM_DATA_CARRIERS = 48
ST_LEN = 160
LT_LEN = 160

data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)

# 加载信号
rx_signal = np.load('recorded_signal_strong.npy')
original_bits = np.load('raw_data.npy')

# === 先估计 CFO，再进行 rx_corrected ===
def estimate_cfo(signal, start):
    sts1 = signal[start + 8*16 : start + 9*16]
    sts2 = signal[start + 9*16 : start + 10*16]
    phase_diff = np.angle(np.vdot(sts1, sts2))
    return phase_diff / (2 * np.pi * 16)

def correct_cfo(signal, cfo):
    n = np.arange(len(signal))
    return signal * np.exp(-1j * 2 * np.pi * cfo * n)

# 估计 CFO 用初始 start 点（2649）
coarse_start = 2649
cfo = estimate_cfo(rx_signal, coarse_start)
rx_corrected = correct_cfo(rx_signal, cfo)
print("Estimated CFO:", cfo)

# === 进行帧起点微调 ===
best_acc = 0
best_offset = 0

for offset in range(-10, 11):
    trial_start = coarse_start + offset
    try:
        # 提取 LTS 做信道估计
        lts1 = rx_corrected[trial_start + ST_LEN + 32: trial_start + ST_LEN + 96]
        lts2 = rx_corrected[trial_start + ST_LEN + 96: trial_start + ST_LEN + 160]
        lts1_freq = np.fft.fftshift(np.fft.fft(lts1, FFT_LEN))
        lts2_freq = np.fft.fftshift(np.fft.fft(lts2, FFT_LEN))
        channel_est = (lts1_freq + lts2_freq) / 2

        # 提取 payload
        payload_start = trial_start + ST_LEN + LT_LEN
        payload = rx_corrected[payload_start:]

        num_symbols = int(np.ceil(len(original_bits) / NUM_DATA_CARRIERS))
        demod_bits = []

        for i in range(num_symbols):
            start_i = i * (CP_LEN + FFT_LEN)
            if start_i + CP_LEN + FFT_LEN > len(payload):
                break
            symbol = payload[start_i + CP_LEN : start_i + CP_LEN + FFT_LEN]
            freq = np.fft.fftshift(np.fft.fft(symbol))
            equalized = freq / channel_est
            data_subcarriers = equalized[data_indices + FFT_LEN // 2]

            # 可选的简单相位修复
            if np.mean(np.real(data_subcarriers)) < 0:
                data_subcarriers *= -1

            bits = (np.real(data_subcarriers) > 0).astype(int)
            demod_bits.extend(bits)

        demod_bits = np.array(demod_bits[:len(original_bits)])
        num_correct = np.sum(demod_bits == original_bits)
        acc = 100 * num_correct / len(original_bits)

        print(f"Offset {offset:+d}: Accuracy = {acc:.2f}%")

        if acc > best_acc:
            best_acc = acc
            best_offset = offset
    except Exception as e:
        print(f"Offset {offset:+d}: ERROR - {str(e)}")

# 最优结果
start = coarse_start + best_offset
print("Best Frame start at:", start)
print(f"Best Accuracy: {best_acc:.2f}%")
