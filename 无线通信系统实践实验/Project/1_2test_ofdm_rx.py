import numpy as np
from ofdm.ofdm_rx import OfdmRx

def main():
    rx = OfdmRx(
        rx_type='socket',
        rx_args=('127.0.0.1', 23456),
        n=64,
        cp_len=16,
        qam_mod_size=2,
        pilot_pattern='custom',
        preamble_type='802.11',
        num_symbol=20,
        verbose=True
    )

    # 读取信号
    print("===== START ")
    samples = np.load("tx_signal_exp1_1.npy")
    print(samples)
    rx.rx_sample_queue.put(samples)
    import time
    #time.sleep(5)
    print("===== %d " % (rx.rx_sample_queue.qsize()))

    # 单次解调
    rx.process()

    # 获取结果
    decoded = rx.get()
    if decoded is not None:
        print("解调成功！bits:")
        print(decoded)
    else:
        print("未能成功解调帧。")

if __name__ == '__main__':
    main()
