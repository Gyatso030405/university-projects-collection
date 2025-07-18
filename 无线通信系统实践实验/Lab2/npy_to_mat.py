import numpy as np
from scipy import io

signal = np.load("tx_signal.npy")
lts = np.load("preamble_lts.npy")
sts = np.load("preamble_sts.npy")
bits = np.load("raw_data.npy")
io.savemat("testdata.mat", {"tx_signal":signal, "preamble_lts":lts, "preamble_sts":sts, "raw_data":bits})
