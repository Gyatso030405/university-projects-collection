import numpy as np
import matplotlib.pyplot as plt
from ofdm.ofdm_tx import OfdmTx


def plot_constellation(freq_symbols, title="QPSK Constellation (Frequency Domain)"):
    """绘制频域星座图"""
    plt.figure(figsize=(8, 8))
    plt.scatter(freq_symbols.real, freq_symbols.imag, alpha=0.6, s=20)
    plt.title(title)
    plt.xlabel("In-phase (I)")
    plt.ylabel("Quadrature (Q)")
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def plot_time_domain(signal, title="OFDM Transmit Samples (Time Domain)"):
    """绘制时域信号"""
    plt.figure(figsize=(12, 6))

    # 绘制实部
    plt.subplot(2, 1, 1)
    plt.plot(signal.real)
    plt.title(f"{title} - Real Part")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)

    # 绘制虚部
    plt.subplot(2, 1, 2)
    plt.plot(signal.imag)
    plt.title(f"{title} - Imaginary Part")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def extract_freq_symbols(tx_samples, ofdm_config):
    """从时域信号中提取频域符号"""
    # 1. 跳过前导码部分
    preamble_length = len(ofdm_config.preamble)
    data_samples = tx_samples[preamble_length:]

    # 2. 计算每个OFDM符号的长度
    symbol_length = ofdm_config.n + ofdm_config.cp_len

    # 3. 计算符号数量
    num_symbols = len(data_samples) // symbol_length

    # 4. 提取频域符号
    freq_symbols = []

    for i in range(num_symbols):
        # 提取一个完整符号
        symbol_start = i * symbol_length
        full_symbol = data_samples[symbol_start:symbol_start + symbol_length]

        # 去掉循环前缀 (CP)
        symbol_without_cp = full_symbol[ofdm_config.cp_len:]

        # FFT转换到频域
        freq_symbol = np.fft.fft(symbol_without_cp, ofdm_config.n)

        # 提取数据子载波
        data_symbols = freq_symbol[ofdm_config.data_sc_index]
        freq_symbols.append(data_symbols)

    # 将所有符号展平
    return np.concatenate(freq_symbols)


if __name__ == '__main__':
    # 创建 OFDM 发送器
    tx = OfdmTx(
        tx_type='socket',
        tx_args=('127.0.0.1', 12345),
        n=64,
        cp_len=16,
        qam_mod_size=2,  # QPSK
        pilot_pattern='custom',
        preamble_type='802.11',
        num_symbol=20,
        verbose=True
    )

    # 构造随机 bit 消息
    bit_length = tx.packet_bit_size
    bin_message = np.random.randint(0, 2, bit_length)

    # 调用 process() 方法，生成 baseband samples
    tx_samples = tx.process(bin_message, is_with_preamble=True)

    # 保存信号
    np.save("tx_signal_exp1_1.npy", tx_samples)
    print(f"信号已保存为 tx_signal_exp1_1.npy, 总长度: {len(tx_samples)} 采样点")

    # 打印关键信息
    print(f"QAM调制后符号数: {len(bin_message) // 2}")  # QPSK 每2bits一个符号

    # 绘制时域信号
    plot_time_domain(tx_samples)

    # 提取并绘制频域星座图
    try:
        freq_symbols = extract_freq_symbols(tx_samples, tx.ofdm_config)
        plot_constellation(freq_symbols)
    except Exception as e:
        print(f"星座图生成错误: {e}")

    # 绘制前导码部分的时域信号
    preamble = tx.ofdm_config.preamble
    plot_time_domain(preamble, "Preamble Signal (Time Domain)")

    # 打印关键参数
    print("\n===== OFDM 配置参数 =====")
    print(f"FFT 点数 (n): {tx.ofdm_config.n}")
    print(f"循环前缀长度 (cp_len): {tx.ofdm_config.cp_len}")
    print(f"调制方式: QPSK (qam_mod_size=2)")
    print(f"数据子载波数量: {len(tx.ofdm_config.data_sc_index)}")
    print(f"前导码长度: {len(preamble)} 采样点")
    print(f"每个OFDM符号总采样点: {tx.ofdm_config.n + tx.ofdm_config.cp_len}")
    print(f"生成符号数量: {tx.num_symbol}")
    print(f"理论信号长度: {len(preamble) + tx.num_symbol * (tx.ofdm_config.n + tx.ofdm_config.cp_len)}")
    print(f"实际信号长度: {len(tx_samples)}")