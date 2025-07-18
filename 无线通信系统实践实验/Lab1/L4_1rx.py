from pluto_interface import pluto_receiver
import numpy as np
import scipy.signal
import time

# PlutoSDR配置
rx_args = "ip:192.168.3.2"
rx_freq = 915e6
bandwidth = 1e6
rx_gain = 0
rx_buffer_size = 10000
gain_control_mode = "fast_attack"
MAX_RUN_TIME = 5  # 程序运行5秒后自动停止

# 加载前导序列（STS）
try:
    preamble_sts = np.load("preamble_sts.npy")
    print(f"Loaded preamble (STS) with length: {len(preamble_sts)}")
except Exception as e:
    print(f"Error loading preamble: {e}")
    exit(1)

# 初始化PlutoSDR接收器
try:
    print("Initializing PlutoSDR receiver...")
    sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain,
                            rx_buffer_size, gain_control_mode).pluto
    print("PlutoSDR receiver initialized successfully")
except TypeError:
    # 如果参数不匹配，尝试不同初始化方式
    sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain,
                            gain_control_mode).pluto
    print("PlutoSDR receiver initialized with default buffer size")


# 用于帧检测的互相关方法
def detect_frames(signal, preamble, threshold_factor=6.0):
    """检测信号中的数据帧起始位置"""
    if len(signal) < len(preamble) * 2:
        return np.array([])

    try:
        # 使用FFT加速的相关计算
        corr = np.abs(scipy.signal.fftconvolve(signal, preamble[::-1].conj(), mode='valid'))

        # 计算噪声基底
        noise_floor = np.mean(corr[:max(1, len(corr) // 20)]) + 1e-10

        # 设置自适应阈值
        threshold = threshold_factor * noise_floor

        # 检测超过阈值的点
        above_threshold = corr > threshold
        start_indices = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1

        return start_indices
    except Exception as e:
        print(f"Detection error: {e}")
        return np.array([])


# 实时帧同步处理
def real_time_frame_sync(runtime=MAX_RUN_TIME):
    """实时帧同步处理主函数"""
    print(f"\nStarting real-time frame synchronization for {runtime} seconds...")
    print("Press Ctrl+C to stop earlier\n")

    # 初始化状态变量
    global_index = 0  # 全局样本索引
    buffer = np.array([], dtype=np.complex64)  # 处理缓冲区
    min_preamble_samples = len(preamble_sts)  # 前导序列所需的最小样本数

    # 数据包计数器
    packet_count = 0

    try:
        start_time = time.time()
        last_update = start_time

        while True:
            # 检查是否超时
            current_time = time.time()
            elapsed = current_time - start_time
            if elapsed >= runtime:
                print(f"\nReached maximum run time of {runtime} seconds")
                break

            # 接收信号块
            received_chunk = sdr_rx.rx()

            # 更新全局索引
            global_index += len(received_chunk)

            # 将新数据添加到缓冲区
            buffer = np.concatenate([buffer, received_chunk])

            # 定期清除过大缓冲区（避免内存溢出）
            if elapsed - last_update > 1.0:  # 每秒检查一次
                if len(buffer) > min_preamble_samples * 20:
                    # 保留最后两个前导序列长度的数据
                    buffer = buffer[-min_preamble_samples * 2:]
                    print(f"Cleared buffer. New size: {len(buffer)} samples")

                # 更新状态
                packets_per_sec = packet_count / elapsed if elapsed > 0 else 0
                print(
                    f"Running: {elapsed:.1f}/{runtime} sec | Packets: {packet_count} | Rate: {packets_per_sec:.2f} pkt/s")
                last_update = current_time

            # 当缓冲区有足够数据时进行帧检测
            if len(buffer) < min_preamble_samples * 3:
                continue

            # 检测帧起始位置
            detections = detect_frames(buffer, preamble_sts)

            # 处理检测结果
            if detections.size > 0:
                # 取最大值作为当前检测（以避免重复检测同一帧）
                current_detection = np.max(detections)

                # 打印检测结果（全局位置）
                packet_pos = global_index - len(buffer) + current_detection
                print(f"Detected frame packet at position: {packet_pos}")
                packet_count += 1

                # 保留检测点之后的数据（清除之前的数据）
                keep_start = min(current_detection + min_preamble_samples, len(buffer))
                buffer = buffer[keep_start:]

    except KeyboardInterrupt:
        print("\nProcessing stopped by user.")
    except Exception as e:
        print(f"Error in processing: {e}")
        # 尝试优雅地处理错误
        try:
            sdr_rx.stop()
            sdr_rx.destroy()
        except:
            pass

    finally:
        elapsed = time.time() - start_time
        print("\n=== Processing Summary ===")
        print(f"Total run time: {elapsed:.2f} seconds")
        print(f"Packets detected: {packet_count}")
        if elapsed > 0:
            print(f"Packet rate: {packet_count / elapsed:.2f} packets/second")

        # 清理资源
        try:
            sdr_rx.stop()
            sdr_rx.destroy()
            print("SDR resources released")
        except Exception as e:
            print(f"Error releasing SDR resources: {e}")


if __name__ == "__main__":
    real_time_frame_sync()