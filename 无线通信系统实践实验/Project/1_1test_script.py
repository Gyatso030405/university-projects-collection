import numpy as np
import matplotlib.pyplot as plt
from ofdm.ofdm_tx import OfdmTx
# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
def main():
    tx = OfdmTx(
        tx_type='socket',
        tx_args=('127.0.0.1', 12345),
        n=64,
        cp_len=16,
        qam_mod_size=2,
        pilot_pattern='custom',
        preamble_type='802.11',
        num_symbol=20,
        verbose=False
    )

    bits = np.random.randint(0, 2, size=(tx.packet_bit_size,))
    samples = tx.process(bits, is_with_preamble=True)

    # 添加噪声前缀用于测试帧同步鲁棒性
    noise_prefix = np.random.randn(500).astype(np.complex128) * 0.1
    signal = np.concatenate((noise_prefix, samples))

    # 保存信号
    np.save("tx_signal_exp1_1.npy", signal)
    print("[Saved] tx_signal_exp1_1.npy with noise prefix + OFDM frame.")

    # 打印 OFDM 参数
    print("\n--- OFDM 配置参数 ---")
    print(f"FFT 点数 (n): {tx.ofdm_config.n}")
    print(f"循环前缀长度 (cp_len): {tx.ofdm_config.cp_len}")
    print(f"调制方式 (QAM): {2**tx.ofdm_config.qam_mod.m}-QAM")
    print(f"数据子载波数量: {tx.ofdm_config.data_sc_num}")
    print(f"前导码长度 (samples): {len(tx.ofdm_config.preamble)}")
    print(f"每个 OFDM 符号总采样数: {tx.ofdm_config.sym_len}")
    print(f"生成符号数量: {tx.num_symbol}")
    print(f"理论信号长度 (无前导码): {tx.num_symbol * tx.ofdm_config.sym_len}")
    print(f"实际发送信号长度: {len(samples)}")

    # 绘制时域波形
    plt.figure(figsize=(10, 4))
    plt.plot(np.real(signal), label='Real')
    plt.plot(np.imag(signal), label='Imag')
    plt.title('发送信号 - 时域波形')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    #plt.savefig("fig_time_signal.png")
    plt.show()
    print("[Saved] fig_time_signal.png")

    # 去除前导码，提取 OFDM 有效符号
    preamble_len = len(tx.ofdm_config.preamble)
    data_signal = samples[preamble_len:]

    sym_len = tx.ofdm_config.n + tx.ofdm_config.cp_len
    num_sym = tx.num_symbol
    symbols = data_signal[:num_sym * sym_len].reshape((num_sym, sym_len))
    no_cp_symbols = symbols[:, tx.ofdm_config.cp_len:]

    # FFT 变换得到频域符号
    freq_symbols = np.fft.fft(no_cp_symbols, axis=1)

    # 提取 QAM 符号（跳过导频）
    qam_symbols = []
    for i in range(num_sym):
        _, data_idx = tx.ofdm_config.ofdm_pilot.get_pilot_and_data_index_at_symbol(i)
        qam_symbols.extend(freq_symbols[i, data_idx])
    qam_symbols = np.array(qam_symbols)

    # 绘制星座图
    plt.figure(figsize=(5, 5))
    plt.scatter(np.real(qam_symbols), np.imag(qam_symbols), s=10, color='blue', alpha=0.7)
    plt.title("频域星座图")
    plt.xlabel("In-Phase")
    plt.ylabel("Quadrature")
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    #plt.savefig("fig_constellation.png")
    plt.show()
    print("[Saved] fig_constellation.png")

if __name__ == '__main__':
    main()
