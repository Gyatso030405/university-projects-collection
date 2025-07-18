import numpy as np
import matplotlib.pyplot as plt

# 加载数据
preamble_lts = np.load("preamble_lts.npy")
preamble_sts = np.load("preamble_sts.npy")
signal_weak = np.load("recorded_signal_weak.npy")
signal_strong = np.load("recorded_signal_strong.npy")

# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. 能量检测 ----------
def energy_detection(signal, threshold_ratio=2.5, window_len=160):
    energy = np.abs(signal) ** 2
    win_energy = np.convolve(energy, np.ones(window_len), mode='valid')
    avg_energy = np.mean(win_energy)
    detected_idxs = np.where(win_energy > avg_energy * threshold_ratio)[0]

    # 去重：移除彼此距离太近的索引（如两帧间隔 < 500 就视为同一帧）
    cleaned_idxs = []
    last_idx = -500
    for idx in detected_idxs:
        if idx - last_idx > 300:
            cleaned_idxs.append(idx)
            last_idx = idx
    return cleaned_idxs, win_energy


# ---------- 2. 双滑动窗口 ----------
def sliding_window_detection(signal, short_len=16, threshold_ratio=2.0):
    energy = np.abs(signal) ** 2
    win_len = short_len
    prev_energy = np.convolve(energy, np.ones(win_len), mode='valid')[:-win_len]
    post_energy = np.convolve(energy[win_len:], np.ones(win_len), mode='valid')

    ratio = post_energy / (prev_energy + 1e-8)
    idxs = np.where(ratio > threshold_ratio)[0]
    cleaned_idxs = []
    last_idx = -500
    for idx in idxs:
        if idx - last_idx > 300:
            cleaned_idxs.append(idx + win_len)
            last_idx = idx
    return cleaned_idxs, ratio


# ---------- 3. 互相关检测 ----------
def cross_correlation_detection(signal, preamble):
    corr = np.abs(np.correlate(signal, preamble, mode='valid'))
    threshold = np.max(corr) * 0.6
    idxs = np.where(corr > threshold)[0]
    cleaned_idxs = []
    last_idx = -500
    for idx in idxs:
        if idx - last_idx > 300:
            cleaned_idxs.append(idx)
            last_idx = idx
    return cleaned_idxs, corr


# ---------- 4. 自相关检测 ----------
def auto_correlation_detection(signal, short_len=16):
    corr_values = []
    for i in range(len(signal) - 2 * short_len):
        seg1 = signal[i: i + short_len]
        seg2 = signal[i + short_len: i + 2 * short_len]
        r = np.abs(np.sum(seg1 * np.conj(seg2))) / (np.linalg.norm(seg1) * np.linalg.norm(seg2) + 1e-8)
        corr_values.append(r)
    corr = np.array(corr_values)
    idxs = np.where(corr > 0.9)[0]
    cleaned_idxs = []
    last_idx = -500
    for idx in idxs:
        if idx - last_idx > 300:
            cleaned_idxs.append(idx)
            last_idx = idx
    return cleaned_idxs, corr


# 对强信号执行四种检测方法
results = {}

results["energy_strong"], energy_curve = energy_detection(signal_strong)
results["sliding_strong"], sliding_curve = sliding_window_detection(signal_strong)
results["cross_strong"], cross_curve = cross_correlation_detection(signal_strong, preamble_lts)
results["auto_strong"], auto_curve = auto_correlation_detection(signal_strong)

# 画图展示每种方法的结果
fig, axs = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
axs[0].plot(energy_curve);
axs[0].set_title("强信号 - 能量检测")
for idx in results["energy_strong"]: axs[0].axvline(idx, color='r', linestyle='--')

axs[1].plot(sliding_curve);
axs[1].set_title("强信号 - 双滑动窗口检测")
for idx in results["sliding_strong"]: axs[1].axvline(idx, color='r', linestyle='--')

axs[2].plot(cross_curve);
axs[2].set_title("强信号 - 互相关检测")
for idx in results["cross_strong"]: axs[2].axvline(idx, color='r', linestyle='--')

axs[3].plot(auto_curve);
axs[3].set_title("强信号 - 自相关检测")
for idx in results["auto_strong"]: axs[3].axvline(idx, color='r', linestyle='--')

plt.tight_layout()
plt.show()

# 对弱信号执行四种检测方法
results["energy_weak"], energy_curve_weak = energy_detection(signal_weak)
results["sliding_weak"], sliding_curve_weak = sliding_window_detection(signal_weak)
results["cross_weak"], cross_curve_weak = cross_correlation_detection(signal_weak, preamble_lts)
results["auto_weak"], auto_curve_weak = auto_correlation_detection(signal_weak)

# 可视化弱信号
fig, axs = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
axs[0].plot(energy_curve_weak);
axs[0].set_title("弱信号 - 能量检测")
for idx in results["energy_weak"]: axs[0].axvline(idx, color='r', linestyle='--')

axs[1].plot(sliding_curve_weak);
axs[1].set_title("弱信号 - 双滑动窗口检测")
for idx in results["sliding_weak"]: axs[1].axvline(idx, color='r', linestyle='--')

axs[2].plot(cross_curve_weak);
axs[2].set_title("弱信号 - 互相关检测")
for idx in results["cross_weak"]: axs[2].axvline(idx, color='r', linestyle='--')

axs[3].plot(auto_curve_weak);
axs[3].set_title("弱信号 - 自相关检测")
for idx in results["auto_weak"]: axs[3].axvline(idx, color='r', linestyle='--')

plt.tight_layout()
plt.show()

results  # 输出强信号各方法检测出的帧起始位置索引

