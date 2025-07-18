import numpy as np
print("Testing numpy IFFT...")
x = np.random.randn(64) + 1j * np.random.randn(64)
y = np.fft.ifft(x)
print("IFFT output:", y)
