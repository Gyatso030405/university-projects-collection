import numpy as np
import matplotlib.pyplot as plt
from ofdm.ofdm_tx import OfdmTx

# 设置图像支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
def main():
    # 初始化 OFDM 发射器
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

    # 生成随机比特序列
    bits = np.random.randint(0, 2, size=(tx.packet_bit_size,))

    # 生成 OFDM 时域基带信号
    samples = tx.process(bits, is_with_preamble=True)

    # 生成随机噪声段（长度可调）
    noise_length = 500
    noise = (np.random.randn(noise_length) + 1j * np.random.randn(noise_length)) * 0.1  # 复数高斯噪声

    # 拼接：噪声段 + 正式OFDM信号
    signal = np.concatenate((noise, samples))

    # 保存结果
    np.save("tx_signal_exp1_1.npy", signal)
    print("[Saved] tx_signal_exp1_1.npy with noise prefix + OFDM frame.")

    # 打印配置参数
    print("\n--- OFDM 配置参数 ---")
    print(f"FFT 点数 (n): {tx.ofdm_config.n}")
    print(f"循环前缀长度 (cp_len): {tx.ofdm_config.cp_len}")
    print(f"调制方式: {2 ** tx.ofdm_config.qam_mod.m}-QAM")
    print(f"数据子载波数量: {tx.ofdm_config.data_sc_num}")
    print(f"前导码长度 (samples): {len(tx.ofdm_config.preamble)}")
    print(f"每个 OFDM 符号总采样数: {tx.ofdm_config.sym_len}")
    print(f"生成符号数量: {tx.num_symbol}")
    print(f"理论信号长度 (不含前导码): {tx.num_symbol * tx.ofdm_config.sym_len}")
    print(f"实际发送信号长度: {len(samples)}")
    print(f"加噪声后的完整信号长度: {len(signal)}")

    # 可视化：时域波形
    plt.figure(figsize=(10, 4))
    plt.plot(np.real(signal), label='Real')
    plt.plot(np.imag(signal), label='Imag')
    plt.title('发送信号 - 时域波形（含随机噪声段）')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    #plt.savefig("fig_time_signal_with_noise.png")
    print("[Saved] fig_time_signal_with_noise.png")


if __name__ == '__main__':
    main()
