import numpy as np
import matplotlib.pyplot as plt

# 设置支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ====== 双滑动窗口检测函数 ======
def detect_preamble_by_sliding_window(signal, short_preamble_len, threshold_ratio=2.5):
    energy = np.abs(signal) ** 2
    win_len = short_preamble_len

    # 用滑动窗求和实现能量滑窗
    prev_energy = np.convolve(energy, np.ones(win_len), mode='valid')[:-win_len]
    post_energy = np.convolve(energy[win_len:], np.ones(win_len), mode='valid')

    # 比较两个窗口能量的比例
    for i in range(len(prev_energy)):
        if prev_energy[i] == 0:
            continue
        ratio = post_energy[i] / prev_energy[i]
        if ratio > threshold_ratio:
            return i + win_len  # 检测到后窗能量突变 → 推断前导码起始
    return None

# ====== 构造测试信号 ======
np.random.seed(123)
signal_len = 1200
short_preamble = np.exp(2j * np.pi * np.random.rand(20))
preamble = np.tile(short_preamble, 10)  # 长度200
preamble_len = len(preamble)
true_start = 550

# 添加噪声和前导码
noise = 0.1 * (np.random.randn(signal_len) + 1j * np.random.randn(signal_len))
signal = noise.copy()
signal[true_start:true_start + preamble_len] += preamble

# ====== 运行检测器 ======
detected_start = detect_preamble_by_sliding_window(signal, short_preamble_len=20)
print(f"检测结果: {detected_start}")

# ====== 画图展示检测过程 ======
energy = np.abs(signal)**2
plt.figure(figsize=(12, 5))
plt.plot(energy, label="信号能量", linewidth=1)
plt.axvline(true_start, color='red', linestyle='--', label=f"真实起始点: {true_start}")
if detected_start is not None:
    plt.axvline(detected_start, color='green', linestyle='--', label=f"检测起始点: {detected_start}")
plt.title("基于双滑动窗口的前导码检测")
plt.xlabel("样本索引")
plt.ylabel("能量")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
