import numpy as np
from ofdm.ofdm_tx import OfdmTx
import time

# 创建发送端
tx = OfdmTx(
    tx_type="socket",
    tx_args=("127.0.0.1", 12345),
    n=64,
    cp_len=16,
    qam_mod_size=2,
    pilot_pattern='custom',
    preamble_type='802.11',
    num_symbol=20,
    verbose=True
)

# 创建一个伪造数据包
bits = np.random.randint(0, 2, 960)  # 符合 packet_bit_size
print("[Test] 发送测试比特流...")
tx.put(bits)

# 等待线程发出
time.sleep(2)
tx.done()

