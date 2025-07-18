if __name__ == '__main__':
    import numpy as np
    from ofdm.ofdm_rx import OfdmRx

    rx = OfdmRx(
        rx_type='socket',
        rx_args=('127.0.0.1', 12345),
        n=64,
        cp_len=16,
        qam_mod_size=2,
        pilot_pattern='custom',
        preamble_type='802.11',
        num_symbol=20,
        verbose=True
    )

    samples = np.load("tx_signal_exp1_1.npy")
    rx.rx_sample_queue.put(samples)

    print("[main] Calling process() once")
    rx.process()

    decoded = rx.get()
    if decoded is not None:
        print("[main] 解调成功，bits:")
        print(decoded)
    else:
        print("[main] 解调失败，未获得bits")
