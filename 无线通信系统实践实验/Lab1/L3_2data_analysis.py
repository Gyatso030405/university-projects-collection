import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """加载信号和前导序列"""
    try:
        signal = np.load("recorded_signal.npy")
        sts = np.load("preamble_sts.npy")
        print(f"已加载信号：长度={len(signal)}, 前导序列长度={len(sts)}")
        return signal, sts
    except Exception as e:
        print(f"数据加载错误: {e}")
        raise


# 1. 能量检测方法（向量化实现）
def energy_detection(signal, window_size=160, threshold_factor=4.0):
    """能量检测方法定位数据包起始位置"""
    # 计算滑动窗口能量（向量化实现）
    energy = np.convolve(np.abs(signal) ** 2, np.ones(window_size), 'valid')

    # 计算噪声基底（使用前5%数据）
    noise_floor = np.mean(energy[:max(1, len(energy) // 20)])
    snr = 10 * np.log10(np.max(energy) / noise_floor) if noise_floor > 1e-10 else 0

    # 设置自适应阈值
    threshold = threshold_factor * noise_floor

    # 检测起始位置（寻找超过阈值的上升沿）
    above_threshold = energy > threshold
    start_indices = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1

    return energy, snr, start_indices


# 2. 双滑动窗口方法（向量化实现）
def dual_window_detection(signal, window_size=160, ratio_threshold=3.0):
    """双滑动窗口方法定位数据包起始位置"""
    # 计算信号能量（预计算）
    sig_power = np.abs(signal) ** 2

    # 计算前导窗口和滞后窗口能量
    leading_energy = np.convolve(sig_power, np.ones(window_size), 'valid')
    lagging_energy = np.convolve(sig_power, np.ones(window_size), 'same')
    lagging_energy = lagging_energy[window_size // 2:len(leading_energy) + window_size // 2]

    # 计算能量比（避免除零错误）
    with np.errstate(divide='ignore', invalid='ignore'):
        energy_ratio = leading_energy / np.maximum(lagging_energy, 1e-10)
    energy_ratio = np.nan_to_num(energy_ratio, posinf=0, neginf=0)

    # 检测起始位置（寻找超过阈值的上升沿）
    above_threshold = energy_ratio > ratio_threshold
    start_indices = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1

    # 验证窗口对齐
    if len(lagging_energy) != len(leading_energy):
        lagging_energy = lagging_energy[:len(leading_energy)]

    return leading_energy, lagging_energy, energy_ratio, start_indices


# 3. 互相关方法（使用快速卷积）
def cross_correlation_detection(signal, preamble):
    """互相关方法定位数据包起始位置"""
    # 使用FFT加速的互相关计算
    corr = np.abs(scipy.signal.fftconvolve(signal, preamble[::-1].conj(), mode='valid'))

    # 计算噪声基底和SNR
    noise_floor = np.mean(corr[:max(1, len(corr) // 20)])
    snr = 10 * np.log10(np.max(corr) / noise_floor) if noise_floor > 1e-10 else 0

    # 设置自适应阈值
    threshold = 6.0 * noise_floor

    # 检测起始位置（寻找超过阈值的上升沿）
    above_threshold = corr > threshold
    start_indices = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1

    return corr, snr, start_indices


# 4. 自相关方法（改进归一化）
def auto_correlation_detection(signal, delay=16, window_size=160, threshold=0.6):
    """自相关方法定位数据包起始位置"""
    # 创建延迟信号（补零对齐）
    delayed_signal = np.zeros_like(signal)
    delayed_signal[delay:] = signal[:-delay]

    # 计算自相关
    corr = np.zeros(len(signal))
    window = np.ones(window_size)

    # 向量化计算相关值
    for i in range(len(signal) - window_size - delay):
        # 仅计算有效范围
        start_idx = i
        end_idx = i + window_size

        # 计算当前窗口的相关
        A = signal[start_idx:end_idx]
        B = delayed_signal[start_idx:end_idx]
        corr_val = np.abs(np.sum(A * B.conj()))

        # 归一化因子（窗口能量乘积的平方根）
        energy_A = np.sum(np.abs(A) ** 2)
        energy_B = np.sum(np.abs(B) ** 2)
        norm_factor = np.sqrt(energy_A * energy_B)

        # 避免除零错误
        if norm_factor > 1e-10:
            corr[i] = corr_val / norm_factor

    # 检测起始位置（寻找超过阈值的上升沿）
    above_threshold = corr > threshold
    start_indices = np.where(np.diff(above_threshold.astype(int)) == 1)[0] + 1

    return corr, start_indices


def run_sync_analysis(signal, sts):
    """运行所有同步方法并分析结果"""
    results = {}

    print("\n===== 同步分析开始 =====")

    # 1. 能量检测
    energy, snr_energy, energy_starts = energy_detection(signal)
    results['Energy Detection'] = {
        'data': energy,
        'starts': energy_starts,
        'snr': snr_energy
    }
    print(f"能量检测: SNR = {snr_energy:.2f} dB, 检测到 {len(energy_starts)} 个数据包: {energy_starts}")

    # 2. 双滑动窗口
    leading, lagging, ratio, dualwin_starts = dual_window_detection(signal)
    results['Dual Window'] = {
        'leading': leading,
        'lagging': lagging,
        'ratio': ratio,
        'starts': dualwin_starts
    }
    print(f"双滑动窗口: 检测到 {len(dualwin_starts)} 个数据包: {dualwin_starts}")

    # 3. 互相关
    cross_corr, snr_cross, cross_starts = cross_correlation_detection(signal, sts)
    results['Cross-Correlation'] = {
        'correlation': cross_corr,
        'starts': cross_starts,
        'snr': snr_cross
    }
    print(f"互相关: SNR = {snr_cross:.2f} dB, 检测到 {len(cross_starts)} 个数据包: {cross_starts}")

    # 4. 自相关
    auto_corr, auto_starts = auto_correlation_detection(signal)
    results['Auto-Correlation'] = {
        'correlation': auto_corr,
        'starts': auto_starts
    }
    print(f"自相关: 检测到 {len(auto_starts)} 个数据包: {auto_starts}")

    print("===== 同步分析完成 =====")
    return results


def plot_results(signal, sts, results):
    """绘制所有同步方法的分析结果"""
    plt.figure(figsize=(14, 12))
    plt.suptitle('数据包同步方法比较', fontsize=16)

    # 原始信号和前导序列互相关
    plt.subplot(5, 1, 1)
    plt.plot(np.abs(signal), 'b-', alpha=0.7, label='信号幅度')

    # 叠加前导序列位置
    if results['Cross-Correlation']['starts'].size > 0:
        for start in results['Cross-Correlation']['starts']:
            plt.axvline(x=start, color='r', linestyle='--', alpha=0.5)
            plt.axvspan(start, start + len(sts), color='r', alpha=0.1)

    plt.title('原始信号与检测到的前导序列位置')
    plt.xlabel('采样点')
    plt.ylabel('幅度')
    plt.legend()

    # 能量检测
    plt.subplot(5, 1, 2)
    plt.plot(results['Energy Detection']['data'], 'g-')
    plt.plot(results['Energy Detection']['starts'],
             results['Energy Detection']['data'][results['Energy Detection']['starts']],
             'ro', markersize=4)
    plt.title(f'能量检测 (SNR={results["Energy Detection"]["snr"]:.2f}dB)')
    plt.xlabel('采样点')
    plt.ylabel('能量')

    # 双滑动窗口
    plt.subplot(5, 1, 3)
    plt.plot(results['Dual Window']['leading'], 'b-', label='前导窗能量')
    plt.plot(results['Dual Window']['lagging'], 'g-', label='滞后窗能量')
    plt.plot(results['Dual Window']['ratio'], 'r-', label='能量比')
    plt.plot(results['Dual Window']['starts'],
             results['Dual Window']['leading'][results['Dual Window']['starts']],
             'ko', markersize=4)
    plt.title('双滑动窗口检测')
    plt.xlabel('采样点')
    plt.ylabel('能量/比率')
    plt.legend()

    # 互相关
    plt.subplot(5, 1, 4)
    plt.plot(results['Cross-Correlation']['correlation'], 'm-')
    plt.plot(results['Cross-Correlation']['starts'],
             results['Cross-Correlation']['correlation'][results['Cross-Correlation']['starts']],
             'ro', markersize=4)
    plt.title(f'互相关检测 (SNR={results["Cross-Correlation"]["snr"]:.2f}dB)')
    plt.xlabel('采样点')
    plt.ylabel('相关系数')

    # 自相关
    plt.subplot(5, 1, 5)
    plt.plot(results['Auto-Correlation']['correlation'], 'c-')
    plt.plot(results['Auto-Correlation']['starts'],
             results['Auto-Correlation']['correlation'][results['Auto-Correlation']['starts']],
             'ro', markersize=4)
    plt.title('自相关检测')
    plt.xlabel('采样点')
    plt.ylabel('归一化相关系数')

    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig('sync_analysis_comparison.png')
    print("分析图表已保存为 'sync_analysis_comparison.png'")
    plt.show()


def main():
    """主函数：执行完整分析流程"""
    try:
        # 加载数据
        signal, sts = load_data()

        # 分析信号
        results = run_sync_analysis(signal, sts)

        # 可视化结果
        plot_results(signal, sts, results)

        return results
    except Exception as e:
        print(f"分析失败: {e}")
        return None


if __name__ == "__main__":
    analysis_results = main()