import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 能量检测函数
def detect_preamble_by_energy(signal, window_len=200, threshold_ratio=2.5):
    """
    在信号中滑动窗口，检测能量变化。返回能量上升超过阈值的位置。
    :param signal: 输入复数信号
    :param window_len: 滑动窗口长度（建议设置为前导码长度或稍长）
    :param threshold_ratio: 突变判断阈值（后窗能量 / 前窗能量）
    :return: 检测到的前导码起始索引 or None
    """
    energy = np.abs(signal)**2
    prev_energy = np.convolve(energy, np.ones(window_len), mode='valid')
    post_energy = np.convolve(energy[window_len:], np.ones(window_len), mode='valid')

    for i in range(len(post_energy)):
        if prev_energy[i] == 0:
            continue
        ratio = post_energy[i] / prev_energy[i]
        if ratio > threshold_ratio:
            return i + window_len  # 能量突变点后推窗口长度
    return None

# ===== 生成测试信号 =====
np.random.seed(42)
signal_len = 1000
short_preamble = np.exp(2j * np.pi * np.random.rand(20))
preamble = np.tile(short_preamble, 10)  # 长度200
preamble_start = 430

# 构造信号
noise = 0.1 * (np.random.randn(signal_len) + 1j * np.random.randn(signal_len))
signal = noise.copy()
signal[preamble_start:preamble_start + len(preamble)] += preamble

# 能量检测
detected_idx = detect_preamble_by_energy(signal, window_len=200)
print(f"检测到的前导码起始位置: {detected_idx}")

# ===== 可视化能量变化 =====
energy = np.abs(signal)**2
plt.figure(figsize=(12, 5))
plt.plot(energy, label='信号能量')
plt.axvline(preamble_start, color='red', linestyle='--', label=f'真实前导码位置：{preamble_start}')
if detected_idx is not None:
    plt.axvline(detected_idx, color='green', linestyle='--', label=f'检测位置：{detected_idx}')
plt.title("使用能量检测法进行前导码检测")
plt.xlabel("样本索引")
plt.ylabel("能量")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
