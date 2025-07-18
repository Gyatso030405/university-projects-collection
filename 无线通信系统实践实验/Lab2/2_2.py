import numpy as np
import matplotlib.pyplot as plt
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 参数
FFT_LEN = 64
CP_LEN = 16
ST_LEN = 160
LT_LEN = 160
NUM_SYMBOLS = 100

data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)
pilot_indices = np.array([-21, -7, 7, 21])

# 帧同步
def frame_sync_sts(signal):
    corr = []
    win = 16
    for i in range(len(signal) - 2 * win):
        p1 = signal[i:i + win]
        p2 = signal[i + win:i + 2 * win]
        corr.append(np.abs(np.vdot(p1, p2)))
    return np.argmax(corr)

# CFO估计与修正
def estimate_cfo(signal, start):
    sts1 = signal[start + 8*16 : start + 9*16]
    sts2 = signal[start + 9*16 : start + 10*16]
    phase_diff = np.angle(np.vdot(sts1, sts2))
    return phase_diff / (2 * np.pi * 16)

def correct_cfo(signal, cfo):
    n = np.arange(len(signal))
    return signal * np.exp(-1j * 2 * np.pi * cfo * n)

# 导入信号
rx_signal = np.load("recorded_signal_100sym.npy")
start = frame_sync_sts(rx_signal)
cfo = estimate_cfo(rx_signal, start)
rx_corrected = correct_cfo(rx_signal, cfo)

# 信道估计
lts_start = start + ST_LEN + 32
lts = rx_corrected[lts_start : lts_start + 64]
lts_freq = np.fft.fftshift(np.fft.fft(lts, FFT_LEN))
channel_est = lts_freq

# 提取有效数据
payload_start = start + ST_LEN + LT_LEN
payload = rx_corrected[payload_start:]

# 逐符号处理
const_points = []
for i in range(NUM_SYMBOLS):
    sym_start = i * (CP_LEN + FFT_LEN)
    if sym_start + CP_LEN + FFT_LEN > len(payload):
        break
    symbol = payload[sym_start + CP_LEN : sym_start + CP_LEN + FFT_LEN]
    freq = np.fft.fftshift(np.fft.fft(symbol))
    equalized = freq / channel_est

    # === 只进行残余CFO的整体相位修正 ===
    pilot_phases = np.angle(equalized[pilot_indices + FFT_LEN // 2])
    avg_phase = np.mean(pilot_phases)
    equalized *= np.exp(-1j * avg_phase)

    data_subcarriers = equalized[data_indices + FFT_LEN // 2]
    const_points.extend(data_subcarriers)

# 星座图绘制
const_points = np.array(const_points)
plt.figure(figsize=(6,6))
plt.scatter(np.real(const_points), np.imag(const_points), alpha=0.6)
plt.title("星座图（仅用导频平均相位补偿，无STO插值）")
plt.xlabel("实部")
plt.ylabel("虚部")
plt.grid(True)
plt.axis("equal")
plt.show()
