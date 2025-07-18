import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']        # 设置中文字体为黑体（SimHei）
plt.rcParams['axes.unicode_minus'] = False          # 正常显示负号

# 前导码检测函数（基于自相关）
def detect_preamble_auto_correlation(signal, short_preamble_len):
    max_corr = 0
    best_idx = None

    for i in range(len(signal) - short_preamble_len - 1):
        seg1 = signal[i : i + short_preamble_len]
        seg2 = signal[i + 1 : i + 1 + short_preamble_len]

        if len(seg2) != short_preamble_len:
            continue

        numerator = np.abs(np.sum(seg1 * np.conj(seg2)))
        denominator = np.sqrt(np.sum(np.abs(seg1)**2) * np.sum(np.abs(seg2)**2))

        corr = numerator / denominator if denominator != 0 else 0

        if corr > max_corr and corr > 0.9:  # 设置阈值过滤噪声
            max_corr = corr
            best_idx = i

    return best_idx

# ===== 生成测试信号 =====
short_preamble_length = 20
signal_length = 1000
short_preamble = np.exp(2j * np.pi * np.random.random(short_preamble_length))
preamble = np.tile(short_preamble, 10)  # 生成重复的前导码

# 添加噪声
noise = np.random.normal(size=signal_length) + 1j * np.random.normal(size=signal_length)
signalA = 0.1 * noise
signalB = 0.1 * noise

# 将前导码插入 signalB 中某个位置
preamble_start_idx = 321
signalB[preamble_start_idx:preamble_start_idx + len(preamble)] += preamble

# ===== 测试检测函数 =====
resultA = detect_preamble_auto_correlation(signalA, short_preamble_length)
resultB = detect_preamble_auto_correlation(signalB, short_preamble_length)

print(f"signalA 检测结果: {resultA}")  # 应该为 None
print(f"signalB 检测结果: {resultB}")  # 应该在 preamble_start_idx 附近

# ===== 画图展示结果 =====
plt.figure(figsize=(12, 5))

plt.subplot(2, 1, 1)
plt.title("SignalA（无前导码）")
plt.plot(np.abs(signalA), label="|SignalA|")
plt.axvline(resultA if resultA else 0, color='r', linestyle='--', label="Detected Start" if resultA else "")
plt.legend()

plt.subplot(2, 1, 2)
plt.title("SignalB（包含前导码）")
plt.plot(np.abs(signalB), label="|SignalB|")
if resultB is not None:
    plt.axvline(resultB, color='g', linestyle='--', label=f"Detected Start: {resultB}")
    plt.axvline(preamble_start_idx, color='r', linestyle='--', label=f"True Start: {preamble_start_idx}")
plt.legend()

plt.tight_layout()
plt.show()
