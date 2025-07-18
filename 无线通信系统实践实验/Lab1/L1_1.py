import numpy as np
import matplotlib.pyplot as plt

def detect_preamble_cross_correlation(preamble, signal):
    threshold = 0.9 * np.sum(np.abs(preamble) ** 2)
    corr = np.correlate(signal, np.conj(preamble), mode='valid')
    power = np.abs(corr)

    for idx, val in enumerate(power):
        if val >= threshold:
            return idx
    return None

def main():
    np.random.seed(0)

    preamble_length = 100
    signal_length = 1000

    preamble = (np.random.random(preamble_length) +
                1j * np.random.random(preamble_length))

    signalA = np.random.random(signal_length) + 1j * np.random.random(signal_length)
    signalB = np.random.random(signal_length) + 1j * np.random.random(signal_length)

    preamble_start_idx = 123
    signalB[preamble_start_idx:preamble_start_idx + preamble_length] = preamble  # 直接覆盖

    resultA = detect_preamble_cross_correlation(preamble, signalA)
    print("signalA detect result:", resultA)
    assert resultA is None

    resultB = detect_preamble_cross_correlation(preamble, signalB)
    print("signalB detect result:", resultB)
    # assert resultB == preamble_start_idx  # 调试阶段可注释
    print("期望位置:", preamble_start_idx)

    corr = np.correlate(signalB, np.conj(preamble), mode='valid')
    plt.figure(figsize=(10, 4))
    plt.plot(np.abs(corr))
    plt.title("Cross-Correlation Magnitude (signalB)")
    plt.xlabel("Sample Index")
    plt.ylabel("Magnitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()

