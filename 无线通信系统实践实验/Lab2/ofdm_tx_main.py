# ofdm_tx_main.py
from ofdm.pluto_interface import pluto_transmitter
from ofdm.ofdm_tx import OfdmTx
import numpy as np
import time

# PlutoSDR TX配置
tx_args = "ip:192.168.3.1"
tx_freq = 915e6
bandwidth = 1e6
tx_gain = -10  # 更高SNR，可调整为 -5 ~ -20

# Pluto发射器和OFDM调制器初始化
sdr_tx = pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto
ofdm_transmitter = OfdmTx(tx_args, tx_freq, bandwidth, tx_gain,
                          n=64, cp_len=16, qam_mod_size=2,  # BPSK
                          pilot_pattern='custom',
                          preamble_type='802.11',
                          num_symbol=100,
                          verbose=True)

# 生成随机数据并保存（方便接收端比对）
raw_data = np.random.randint(0, 2, 4800)
np.save("raw_data.npy", raw_data)

# OFDM调制
OFDM_packet = ofdm_transmitter.process(raw_data)
transmitted_signal = OFDM_packet * (2 ** 14)

# 设置周期发送
sdr_tx.tx_cyclic_buffer = True
sdr_tx.tx(transmitted_signal)
print("发送启动，数据包持续循环发送中。")
