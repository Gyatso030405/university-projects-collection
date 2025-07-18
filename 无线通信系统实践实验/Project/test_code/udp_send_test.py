import socket
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target = ("127.0.0.1", 52002)

samples = (np.random.randn(1000) + 1j * np.random.randn(1000)).astype(np.complex128)
sock.sendto(samples.tobytes(), target)
print("[UDP Send Test] Sent.")
