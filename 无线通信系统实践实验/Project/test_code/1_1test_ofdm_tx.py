import numpy as np
import matplotlib.pyplot as plt
from ofdm.ofdm_tx import OfdmTx

# -----------------------
# 模拟发送一个随机消息
# -----------------------

if __name__ == '__main__':
    # 创建 OFDM 发送器
    tx = OfdmTx(
        tx_type='socket',                       # 这里随便填，测试用不发出去
        tx_args=('127.0.0.1', 12345),           # 用不到 socket，随便填
        n=64,
        cp_len=16,
        qam_mod_size=2,                         # QPSK
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

    np.save("tx_signal_exp1_1.npy", tx_samples)
    print("信号已保存为 tx_signal_exp1_1.npy")

    # -----------------------
    # 绘制结果图像
    # -----------------------

    # 实部、虚部时域图
    plt.figure(figsize=(10, 4))
    plt.plot(tx_samples.real, label='Real')
    plt.plot(tx_samples.imag, label='Imag')
    plt.title("OFDM Transmit Samples (Time Domain)")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 星座图（只画数据部分）
    data_start = len(tx.ofdm_config.preamble)
    symbols = tx_samples[data_start:]
    symbols_per_symbol = tx.ofdm_config.n + tx.ofdm_config.cp_len
    symbols = symbols.reshape(-1, symbols_per_symbol)
    data_symbols = symbols[:, tx.ofdm_config.cp_len:]  # 去掉CP
    data_symbols = data_symbols.flatten()

    plt.figure(figsize=(4, 4))
    plt.plot(data_symbols.real, data_symbols.imag, '.', alpha=0.5)
    plt.title("Constellation After Modulation (Raw Time Domain)")
    plt.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
