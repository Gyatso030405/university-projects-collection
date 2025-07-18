import numpy as np
from ofdm.ofdm_tx import OfdmTx

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

    noise_prefix = np.random.randn(500).astype(np.complex128) * 0.1
    signal = np.concatenate((noise_prefix, samples))

    np.save("tx_signal_exp1_1.npy", signal)
    print("[Saved] tx_signal_exp1_1.npy with noise prefix + OFDM frame.")

if __name__ == '__main__':
    main()

