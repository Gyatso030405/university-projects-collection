import matplotlib.pyplot as plt
import numpy as np
import time
from pluto_interface import pluto_transmitter

# PlutoSDR参数配置
tx_args = "ip:192.168.3.1"
tx_freq = 915e6
bandwidth = 1e6
tx_gain = -60
sample_rate = 1e6  # 采样率1MHz

# 初始化发送端
ssdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto

# 加载并准备发送信号
transmitted_signal = np.load("tx_signal.npy")
transmitted_signal = transmitted_signal * (2 ** 14)

frame_len = 1600  # 每个数据包的采样点数
num_packets_per_tx = len(transmitted_signal) // frame_len
print(f"发送信号总长度: {len(transmitted_signal)} 采样点")
print(f"每次发射中包含的数据包数量: {num_packets_per_tx}")
print(f"每次发射持续时间: {len(transmitted_signal) / sample_rate:.4f} 秒")

# 目标发送速率：15包/秒（低于20包/秒）
target_packets_per_second = 15

# 计算每次发送后需要等待的时间
# 每次发送包含的数据包数 * 每个包的持续时间 = 每次发送的持续时间
tx_duration = num_packets_per_tx * (frame_len / sample_rate)

# 计算需要等待的时间以达到目标速率
# 目标间隔 = 1 / 目标速率
# 需要等待时间 = 目标间隔 - 发送持续时间
wait_time = (1 / target_packets_per_second) - tx_duration

if wait_time < 0:
    print(f"警告：当前配置无法达到目标速率 {target_packets_per_second} 包/秒")
    print(f"建议减少每次发送的数据包数量或降低目标速率")
    # 设置最小等待时间为10ms
    wait_time = 0.01
else:
    print(f"为达到 {target_packets_per_second} 包/秒，每次发送后需等待 {wait_time:.4f} 秒")

# 统计总发送的数据包数量
total_packets_sent = 0

# 循环发送
loop_count = 0
start_time = time.time()

try:
    while loop_count < 10000:
        # 准确测量发送时间
        tx_start = time.time()
        sdr_tx.tx(transmitted_signal)
        actual_tx_duration = time.time() - tx_start

        total_packets_sent += num_packets_per_tx
        loop_count += 1

        # 计算实际传输速率
        current_time = time.time()
        elapsed = current_time - start_time
        actual_rate = total_packets_sent / elapsed

        # 等待以达到目标速率
        adjusted_wait = max(0, wait_time - (time.time() - tx_start - actual_tx_duration))
        time.sleep(adjusted_wait)

        if loop_count % 10 == 0:
            print(f"[INFO] 第 {loop_count} 次发送 | "
                  f"累计数据包: {total_packets_sent} | "
                  f"实际速率: {actual_rate:.1f} 包/秒 | "
                  f"发送耗时: {actual_tx_duration * 1000:.2f}ms | "
                  f"等待: {adjusted_wait * 1000:.2f}ms")

except KeyboardInterrupt:
    print("\n发送被用户中断")

finally:
    # 统计最终结果
    elapsed = time.time() - start_time
    print("\n=== 发送统计 ===")
    print(f"总运行时间: {elapsed:.2f} 秒")
    print(f"总发送数据包: {total_packets_sent}")
    print(f"平均发送速率: {total_packets_sent / elapsed:.1f} 包/秒")

    # 释放资源
    try:
        sdr_tx.stop()
        sdr_tx.destroy()
        print("SDR资源已释放")
    except Exception as e:
        print(f"释放资源时出错: {e}")

# 可视化发送信号
plt.figure(figsize=(12, 4))
plt.plot(np.abs(transmitted_signal))
plt.title(f"Transmitted Signal ({len(transmitted_signal)} samples)")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("tx_signal_visualization.png")
plt.show()
