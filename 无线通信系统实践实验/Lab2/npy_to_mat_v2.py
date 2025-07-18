import numpy as np
from scipy.io import savemat

# 载入
signal_10 = np.load("recorded_signal_10sym.npy")
signal_100 = np.load("recorded_signal_100sym.npy")

# 转换保存
savemat("recorded_signal_10sym.mat", {"rx10": signal_10})
savemat("recorded_signal_100sym.mat", {"rx100": signal_100})
