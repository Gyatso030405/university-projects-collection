import numpy as np
import matplotlib.pyplot as plt

# 参数设定
FFT_LEN = 64
CP_LEN = 16
NUM_DATA_CARRIERS = 48

# 子载波索引
#pilot_indices = np.array([-21, -7, 7, 21])
data_indices = np.array(
    list(range(1, 7)) +          # 1 ~ 6
    list(range(8, 21)) +         # 8 ~ 20
    list(range(22, 27)) +        # 22 ~ 26
    list(range(-26, -21)) +      # -26 ~ -22
    list(range(-20, -7)) +       # -20 ~ -8
    list(range(-6, 0))           # -6 ~ -1
)

# 载入发送信号与原始数据
rx_signal = np.load('tx_signal.npy')
original_bits = np.load('raw_data.npy')

# 读取STS（160 samples），LTS（160 samples）后即为数据符号
sts_len = 160
lts_len = 160
payload_start = sts_len + lts_len 

# 提取LTS信号（用于信道估计）
lts_time = rx_signal[sts_len : sts_len + 160]
lts1 = lts_time[32:96]  # 取前一个LTS（不含CP）
lts2 = lts_time[96:160]  # 取后一个LTS

lts1_freq = np.fft.fftshift(np.fft.fft(lts1, n=FFT_LEN))
lts2_freq = np.fft.fftshift(np.fft.fft(lts2, n=FFT_LEN))

known_lts_freq = (lts1_freq + lts2_freq) / 2  # 理论上应有已知LTS，但此处使用接收的（无失真）

# 提取数据区域
payload = rx_signal[payload_start:]

# 切片为多个符号，每个包含 CP + FFT
ofdm_symbols = []
i = 0
while i + CP_LEN + FFT_LEN <= len(payload):
    symbol = payload[i + CP_LEN:i + CP_LEN + FFT_LEN]
    ofdm_symbols.append(symbol)
    i += CP_LEN + FFT_LEN

ofdm_symbols = np.array(ofdm_symbols)


num_symbols_needed = int(np.ceil(len(original_bits) / NUM_DATA_CARRIERS))
ofdm_symbols = ofdm_symbols[:num_symbols_needed]  # 只保留足够数量的符号

# FFT 并进行信道均衡
demod_bits = []
for symbol in ofdm_symbols:
    symbol_freq = np.fft.fftshift(np.fft.fft(symbol))
    equalized = symbol_freq / known_lts_freq  # 信道均衡
    data_subcarriers = equalized[data_indices + FFT_LEN // 2]  # 偏移+32
    bits = np.real(data_subcarriers) > 0  # BPSK 判决
    demod_bits.extend(bits.astype(int))

demod_bits = np.array(demod_bits[:len(original_bits)])  # 修剪长度一致

# 输出正确率
num_correct = np.sum(demod_bits == original_bits)
accuracy = num_correct / len(original_bits) * 100
print(f"解调完成！总比特数: {len(original_bits)}, 正确数: {num_correct}, 准确率: {accuracy:.2f}%")


#  排查
#  检查载波索引是否正确
print("data_indices:", data_indices)
print("len(data_indices):", len(data_indices))  # 应该是48
#   检查 payload 开始位置是否正确
print("Payload start index:", payload_start)
print("rx_signal length:", len(rx_signal))
#   第一组 OFDM 符号的时域波形：
plt.plot(np.real(payload[:80]))
plt.title("First OFDM Symbol (Time Domain)")
plt.grid()
plt.show()

#  验证频域符号与信道估计是否正常
plt.scatter(np.real(data_subcarriers), np.imag(data_subcarriers))
plt.title("Demodulated Data Subcarriers")
plt.xlabel("Real")
plt.ylabel("Imag")
plt.grid()
plt.show()   #正常情况下都集中在 +1 / -1 处的实轴两侧

print("接收到的OFDM符号数:", len(ofdm_symbols))
print("原始数据比特数:", len(original_bits))
print("每个符号比特数:", NUM_DATA_CARRIERS)
print("理论需要符号数:", int(np.ceil(len(original_bits) / NUM_DATA_CARRIERS)))
