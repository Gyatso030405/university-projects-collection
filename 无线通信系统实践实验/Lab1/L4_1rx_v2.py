import numpy as np
import matplotlib.pyplot as plt
import time
from pyadi_iio import Pluto

# ---------- PlutoSDR 接收参数 ----------
rx_args = "ip:192.168.3.1"  # 第二台Pluto的IP地址
rx_freq = 915e6
sample_rate = 1e6
rx_bandwidth = 1e6
rx_gain = 40  # 适中接收增益，调节信噪比

# ---------- 加载前导码 ----------
preamble = np.load("preamble_lts.npy")  # 使用与发送端相同的前导码
frame_len = 1600  # 每个帧的采样点数（包括数据）

# ---------- 初始化接收设备 ----------
sdr_rx = Pluto(uri=rx_args)
sdr_rx.rx_enabled_channels = [0]
sdr_rx.sample_rate = int(sample_rate)
sdr_rx.rx_lo = int(rx_freq)
sdr_rx.rx_rf_bandwidth = int(rx_bandwidth)
sdr_rx.rx_hardwaregain_chan0 = int(rx_gain)
sdr_rx.rx_buffer_size = 8192  # 接收缓冲区
print("[INFO] Pluto SDR 接收端已初始化")

# ---------- 包统计变量 ----------
total_packets_received = 0
packets_last_second = 0
start_time = time.time()
last_print_time = start_time

# ---------- 实时接收循环 ----------
try:
    while True:
        raw = sdr_rx.rx()  # 读取一个数据块（复数）
        data = np.array(raw)

        # --- 帧同步检测（互相关） ---
        corr = np.abs(np.correlate(data, preamble, mode='valid'))
        threshold = np.max(corr) * 0.6
        detected_idxs = np.where(corr > threshold)[0]

        # --- 去重（相邻索引归为一帧） ---
        cleaned = []
        last = -frame_len
        for idx in detected_idxs:
            if idx - last > frame_len // 2:
                cleaned.append(idx)
                last = idx

        packets_detected = len(cleaned)
        total_packets_received += packets_detected
        packets_last_second += packets_detected

        # 每秒显示一次速率
        now = time.time()
        if now - last_print_time >= 1.0:
            print(f"[{now - start_time:.1f}s] 本秒接收: {packets_last_second} 包 | 累计接收: {total_packets_received} 包")
            last_print_time = now
            packets_last_second = 0

except KeyboardInterrupt:
    print("\n[INFO] 接收中断，退出程序")

finally:
    del sdr_rx  # 释放SDR资源
    print("[INFO] 接收结束，Pluto SDR 资源已释放")
