import numpy as np
import matplotlib.pyplot as plt
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 1. 加载数据
tx0 = np.load("fixed_packet_0.npy")
tx1 = np.load("fixed_packet_1.npy")
rx = np.load("received_signal.npy")

# 2. 归一化
def normalize(sig):
    return sig / np.max(np.abs(sig))

tx0 = normalize(tx0)
tx1 = normalize(tx1)
rx = normalize(rx)

# 3. 匹配函数：滑动窗口搜索最大相关性
def find_match(tx, rx):
    max_corr = 0
    best_index = -1
    for i in range(len(rx) - len(tx)):
        segment = rx[i:i+len(tx)]
        corr = np.abs(np.sum(np.conj(tx) * segment))
        if corr > max_corr:
            max_corr = corr
            best_index = i
    return best_index, max_corr


# 4. 查找 tx0 和 tx1 在接收信号中的位置
idx0, corr0 = find_match(tx0, rx)
idx1, corr1 = find_match(tx1, rx)

# 5. 结果输出
print(f"Packet 0 匹配位置: {idx0}, 相似度: {corr0:.2f}")
print(f"Packet 1 匹配位置: {idx1}, 相似度: {corr1:.2f}")

# 6. 可视化（对比每个 packet 与 rx 对应段）
plt.figure(figsize=(12, 5))

plt.subplot(2, 1, 1)
plt.plot(np.real(tx0), label="TX Packet 0 (Real)")
plt.plot(np.real(rx[idx0:idx0+len(tx0)]), '--', label="RX Matched (Real)")
plt.title("Packet 0 对比")
plt.legend()
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(np.real(tx1), label="TX Packet 1 (Real)")
plt.plot(np.real(rx[idx1:idx1+len(tx1)]), '--', label="RX Matched (Real)")
plt.title("Packet 1 对比")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
