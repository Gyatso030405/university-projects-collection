import numpy as np
import matplotlib.pyplot as plt
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 参数设置
FFT_LEN = 64
CP_LEN = 16
ST_LEN = 160
LT_LEN = 160
data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)

def frame_sync_sts(signal):
    corr = []
    win = 16
    for i in range(len(signal) - 2 * win):
        p1 = signal[i:i + win]
        p2 = signal[i + win:i + 2 * win]
        corr.append(np.abs(np.vdot(p1, p2)))
    return np.argmax(corr)

def estimate_cfo(signal, start):
    sts1 = signal[start + 8*16 : start + 9*16]
    sts2 = signal[start + 9*16 : start + 10*16]
    phase_diff = np.angle(np.vdot(sts1, sts2))
    return phase_diff / (2 * np.pi * 16)

def correct_cfo(signal, cfo):
    n = np.arange(len(signal))
    return signal * np.exp(-1j * 2 * np.pi * cfo * n)

def extract_symbols(rx_signal, start, offset):
    # 偏移调整后的有效载荷起始位置
    payload_start = start + ST_LEN + LT_LEN
    payload = rx_signal[payload_start:]
    symbols = []
    for i in range(10):  # 10个OFDM符号
        sym_start = i * (CP_LEN + FFT_LEN)
        if sym_start + CP_LEN + FFT_LEN > len(payload):
            break
        # 改变CP去除位置
        symbol = payload[sym_start + CP_LEN + offset : sym_start + CP_LEN + offset + FFT_LEN]
        if len(symbol) == FFT_LEN:
            symbols.append(symbol)
    return np.array(symbols)

def estimate_channel(rx_signal, start, offset):
    # 使用LTS做信道估计
    lts = rx_signal[start + ST_LEN + 32 + offset : start + ST_LEN + 32 + offset + FFT_LEN]
    lts_freq = np.fft.fftshift(np.fft.fft(lts, FFT_LEN))
    return lts_freq

# === 主流程 ===
rx = np.load("recorded_signal_10sym.npy")
start = frame_sync_sts(rx)
cfo = estimate_cfo(rx, start)
rx_corr = correct_cfo(rx, cfo)

# === 两种位置的CP去除偏移 ===
offset_a = 0
offset_b = 2

ch_a = estimate_channel(rx_corr, start, offset_a)
ch_b = estimate_channel(rx_corr, start, offset_b)

# 绘制信道幅度与相位对比
freq_axis = np.fft.fftshift(np.fft.fftfreq(FFT_LEN, d=1))
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(freq_axis, np.abs(ch_a), label="Offset 0")
plt.plot(freq_axis, np.abs(ch_b), label="Offset 2")
plt.title("信道幅度")
plt.xlabel("子载波索引")
plt.legend()
plt.grid()

plt.subplot(1, 2, 2)
plt.plot(freq_axis, np.angle(ch_a), label="Offset 0")
plt.plot(freq_axis, np.angle(ch_b), label="Offset 2")
plt.title("信道相位")
plt.xlabel("子载波索引")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# 相位差
phase_diff = np.unwrap(np.angle(ch_b)) - np.unwrap(np.angle(ch_a))
plt.plot(freq_axis, phase_diff)
plt.title("Offset=2 与 Offset=0 的信道相位差")
plt.xlabel("子载波索引")
plt.ylabel("相位差（弧度）")
plt.grid()
plt.show()

# 幅度差曲线（abs(H_offset2) - abs(H_offset0)）
amp_diff = np.abs(np.abs(ch_b) - np.abs(ch_a))

plt.figure()
plt.plot(freq_axis, amp_diff)
plt.title("信道幅度差 (Offset=2 - Offset=0)")
plt.xlabel("子载波索引")
plt.ylabel("幅度差")
plt.grid()
plt.show()

# 计算均方误差 MSE 和标准差 STD
mse = np.mean(amp_diff ** 2)
std = np.std(amp_diff)
print(f"信道幅度差 MSE: {mse:.6f}")
print(f"信道幅度差 Std Dev: {std:.6f}")
