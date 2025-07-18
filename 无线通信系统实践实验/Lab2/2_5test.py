import numpy as np
import matplotlib.pyplot as plt
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 参数设置
FFT_LEN = 64
CP_LEN = 16
ST_LEN = 160  # 10 * 16
LT_LEN = 160  # 32 + 64 + 64
NUM_SYMBOLS = 10  # 10个OFDM符号
data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)

# 载入信号
rx_signal = np.load('recorded_signal_10sym.npy')

# 帧起始位置（你已通过 frame_sync_sts 找到）
frame_start = 2649  # 示例值，请根据你实验的结果修改！

# 提取 LTS 并估计信道（此处 LTS 不加 offset，保持固定）
lts1 = rx_signal[frame_start + ST_LEN + 32 : frame_start + ST_LEN + 96]
lts2 = rx_signal[frame_start + ST_LEN + 96 : frame_start + ST_LEN + 160]
lts1_freq = np.fft.fftshift(np.fft.fft(lts1, FFT_LEN))
lts2_freq = np.fft.fftshift(np.fft.fft(lts2, FFT_LEN))
channel_est = (lts1_freq + lts2_freq) / 2

# 用于绘图的频率坐标
freq_axis = np.arange(-FFT_LEN // 2, FFT_LEN // 2)

# ===== 提取不同 offset 下的符号数据并估计信道幅度与相位 =====
def extract_channel_estimates(rx, offset):
    payload_start = frame_start + ST_LEN + LT_LEN
    ch_list = []
    for i in range(NUM_SYMBOLS):
        base = payload_start + i * (CP_LEN + FFT_LEN)
        symbol = rx[base + CP_LEN + offset : base + CP_LEN + offset + FFT_LEN]
        symbol_fft = np.fft.fftshift(np.fft.fft(symbol, FFT_LEN))
        ch = symbol_fft / channel_est  # 信道均衡后符号
        ch_list.append(ch)
    return np.array(ch_list)

# 获取 offset=0 和 offset=2 的结果
ch_offset_0 = extract_channel_estimates(rx_signal, offset=0)
ch_offset_2 = extract_channel_estimates(rx_signal, offset=2)

# 平均每个符号的结果（仅看第一个符号即可）
H0 = ch_offset_0[0]
H2 = ch_offset_2[0]

# ====== 绘制信道幅度 ======
plt.figure()
plt.plot(freq_axis, np.abs(H0), label='Offset = 0')
plt.plot(freq_axis, np.abs(H2), label='Offset = 2')
plt.title("信道幅度比较")
plt.xlabel("子载波索引")
plt.ylabel("|H(f)|")
plt.legend()
plt.grid()

# ====== 绘制信道相位 ======
plt.figure()
plt.plot(freq_axis, np.angle(H0), label='Offset = 0')
plt.plot(freq_axis, np.angle(H2), label='Offset = 2')
plt.title("信道相位比较")
plt.xlabel("子载波索引")
plt.ylabel("Phase(H(f))")
plt.legend()
plt.grid()

# ====== 绘制相位差 ======
plt.figure()
phase_diff = np.angle(H2) - np.angle(H0)
# 将相位差归一化到 [-pi, pi]
phase_diff = (phase_diff + np.pi) % (2 * np.pi) - np.pi
plt.plot(freq_axis, phase_diff)
plt.title("信道相位差 (Offset=2 - Offset=0)")
plt.xlabel("子载波索引")
plt.ylabel("相位差 (rad)")
plt.grid()

# ====== 统计差异 ======
amp_diff = np.abs(np.abs(H2) - np.abs(H0))
mse = np.mean(amp_diff ** 2)
std = np.std(amp_diff)

print(f"信道幅度差 MSE: {mse:.6f}")
print(f"信道幅度差 Std Dev: {std:.6f}")

plt.figure()
plt.plot(freq_axis, amp_diff)
plt.title("信道幅度差 |H2| - |H0|")
plt.xlabel("子载波索引")
plt.ylabel("幅度差")
plt.grid()
plt.show()

from scipy.stats import linregress

# phase_diff 是 [-pi, pi] 范围的相位差
unwrapped = np.unwrap(phase_diff)
slope, intercept, r_value, _, _ = linregress(freq_axis, unwrapped)

print(f"线性拟合 R²: {r_value ** 2:.4f}, 斜率: {slope:.4f}")

