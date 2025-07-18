import numpy as np

# ===== 参数设置 =====
FFT_LEN = 64
CP_LEN = 16
NUM_DATA_CARRIERS = 48
ST_LEN = 160
LT_LEN = 160

# ===== 数据子载波索引（共48个）=====
data_indices = np.array(
    list(range(1, 7)) + list(range(8, 21)) + list(range(22, 27)) +
    list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0))
)

# ===== 帧同步函数 =====
def frame_sync_sts(signal):
    corr = []
    win = 16
    for i in range(len(signal) - 2 * win):
        p1 = signal[i:i + win]
        p2 = signal[i + win:i + 2 * win]
        corr.append(np.abs(np.vdot(p1, p2)))
    return np.argmax(corr)

# ===== CFO估计与补偿函数 =====
def estimate_cfo(signal, start):
    sts1 = signal[start + 8*16 : start + 9*16]
    sts2 = signal[start + 9*16 : start + 10*16]
    phase_diff = np.angle(np.vdot(sts1, sts2))
    return phase_diff / (2 * np.pi * 16)

def correct_cfo(signal, cfo):
    n = np.arange(len(signal))
    return signal * np.exp(-1j * 2 * np.pi * cfo * n)

# ===== 解调主流程函数 =====
def ofdm_rx(signal, num_symbols, save_path):
    start = frame_sync_sts(signal)
    cfo = estimate_cfo(signal, start)
    print(f"[{save_path}] Frame start: {start}, Estimated CFO: {cfo:.5f}")
    signal_corrected = correct_cfo(signal, cfo)

    # 信道估计
    lts_start = start + ST_LEN + 32
    lts = signal_corrected[lts_start : lts_start + 64]
    lts_freq = np.fft.fftshift(np.fft.fft(lts, FFT_LEN))
    channel_est = lts_freq

    # 提取数据
    payload_start = start + ST_LEN + LT_LEN
    payload = signal_corrected[payload_start:]
    demod_bits = []

    for i in range(num_symbols):
        start_i = i * (CP_LEN + FFT_LEN)
        if start_i + CP_LEN + FFT_LEN > len(payload):
            break
        symbol = payload[start_i + CP_LEN : start_i + CP_LEN + FFT_LEN]
        freq = np.fft.fftshift(np.fft.fft(symbol))
        equalized = freq / channel_est
        data_subcarriers = equalized[data_indices + FFT_LEN // 2]
        bits = (np.real(data_subcarriers) > 0).astype(int)
        demod_bits.extend(bits)

    demod_bits = np.array(demod_bits)
    print(f"[{save_path}] 解调完成！比特数: {len(demod_bits)}")
    np.save(save_path, demod_bits)

# ===== 解调两个文件 =====
rx_10sym = np.load("recorded_signal_10sym.npy")
ofdm_rx(rx_10sym, 10, "decoded_bits_10sym.npy")

rx_100sym = np.load("recorded_signal_100sym.npy")
ofdm_rx(rx_100sym, 100, "decoded_bits_100sym.npy")
