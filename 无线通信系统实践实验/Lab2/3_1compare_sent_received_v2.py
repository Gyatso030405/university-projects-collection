import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 加载发送与接收信号
tx0 = np.load("raw_data_0.npy")
tx1 = np.load("raw_data_1.npy")
rx = np.load("received_signal.npy")

# === 步骤1：归一化 ===
def normalize(x):
    return x / np.linalg.norm(x)

tx0 = normalize(tx0)
tx1 = normalize(tx1)
rx = rx / np.max(np.abs(rx))  # 不使用norm防止衰减过大

# === 步骤2：匹配函数 ===
def match_packet(tx, rx, label="Packet"):
    correlation = np.abs(correlate(rx, tx, mode='valid'))
    best_index = np.argmax(correlation)
    similarity = correlation[best_index]

    print(f"{label} 匹配位置: {best_index}, 最大归一化相关: {similarity:.4f}")

    # 绘图验证匹配
    plt.figure(figsize=(12, 4))
    plt.plot(np.real(rx[best_index:best_index + len(tx)]), label="RX Segment")
    plt.plot(np.real(tx), label="TX Packet", linestyle='--')
    plt.title(f"{label} 匹配位置: {best_index}, 相似度: {similarity:.4f}")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# === 步骤3：执行匹配 ===
match_packet(tx0, rx, label="Packet 0")
match_packet(tx1, rx, label="Packet 1")
