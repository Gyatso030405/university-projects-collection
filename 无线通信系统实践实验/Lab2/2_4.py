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

data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)


# 帧同步（使用STS相关性）
def frame_sync_sts(signal):
    corr = []
    win = 16
    for i in range(len(signal) - 2 * win):
        p1 = signal[i:i + win]
        p2 = signal[i + win:i + 2 * win]
        corr.append(np.abs(np.vdot(p1, p2)))
    return np.argmax(corr)


# 主函数：不做CFO补偿 & 不做相位追踪
def plot_no_cfo_no_phase_track(filename, num_symbols):
    rx_signal = np.load(filename)
    start = frame_sync_sts(rx_signal)

    # === 不进行CFO估计与修正 ===
    rx_corrected = rx_signal.copy()

    # === 信道估计 ===
    lts_start = start + ST_LEN + 32
    lts = rx_corrected[lts_start: lts_start + 64]
    lts_freq = np.fft.fftshift(np.fft.fft(lts, FFT_LEN))
    channel_est = lts_freq

    # === 提取有效数据 ===
    payload_start = start + ST_LEN + LT_LEN
    payload = rx_corrected[payload_start:]

    # === 星座图绘制 ===
    const_points = []
    for i in range(num_symbols):
        sym_start = i * (CP_LEN + FFT_LEN)
        if sym_start + CP_LEN + FFT_LEN > len(payload):
            break
        symbol = payload[sym_start + CP_LEN: sym_start + CP_LEN + FFT_LEN]
        freq = np.fft.fftshift(np.fft.fft(symbol))
        equalized = freq / channel_est
        data_subcarriers = equalized[data_indices + FFT_LEN // 2]
        const_points.extend(data_subcarriers)

    const_points = np.array(const_points)
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(const_points), np.imag(const_points), alpha=0.6)
    plt.title(f"星座图（{filename}，无CFO补偿，无相位追踪）")
    plt.xlabel("实部")
    plt.ylabel("虚部")
    plt.grid(True)
    plt.axis("equal")
    plt.show()


# === 执行两种信号 ===
plot_no_cfo_no_phase_track("recorded_signal_10sym.npy", num_symbols=10)
plot_no_cfo_no_phase_track("recorded_signal_100sym.npy", num_symbols=100)
