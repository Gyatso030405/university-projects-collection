import matplotlib.pyplot as plt
import numpy as np
import time
from pluto_interface import pluto_transmitter

# PlutoSDR参数配置
tx_args = "ip:192.168.3.1"
tx_freq = 915e6
bandwidth = 1e6
tx_gain = -60

# 初始化发送端
sdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto

# 加载并准备发送信号
transmitted_signal = np.load("tx_signal.npy")
transmitted_signal = transmitted_signal * (2 ** 14)

frame_len = 1600  # 每个数据包的采样点数
num_packets_per_tx = len(transmitted_signal) // frame_len
print("每次发射中包含的数据包数量：", num_packets_per_tx)

# 总计发送统计
total_packets_sent = 0
loop_count = 0

# 秒级速率统计
start_time = time.time()
last_print_time = start_time
packets_last_second = 0

# 循环发送
while loop_count < 10000:
    sdr_tx.tx(transmitted_signal)
    total_packets_sent += num_packets_per_tx
    packets_last_second += num_packets_per_tx
    loop_count += 1

    current_time = time.time()

    # 每秒打印一次速率信息
    if current_time - last_print_time >= 1.0:
        elapsed = current_time - start_time
        print(f"[{elapsed:.1f}s] 第 {loop_count} 次发送 | "
              f"本秒发送: {packets_last_second} 包 | "
              f"累计发送: {total_packets_sent} 包")
        last_print_time = current_time
        packets_last_second = 0  # 重置本秒计数

    time.sleep(0.01)

# 可视化发送信号
x = np.arange(len(transmitted_signal))
plt.plot(x, np.abs(transmitted_signal))
plt.title("Transmitted Signal")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid(True)
plt.savefig("output.png")
plt.show()
