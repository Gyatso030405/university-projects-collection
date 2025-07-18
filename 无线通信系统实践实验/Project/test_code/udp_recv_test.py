import socket
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 52002))
print("[UDP Recv Test] Listening on 52002...")

data, addr = sock.recvfrom(65507)
samples = np.frombuffer(data, dtype=np.complex128)
print(f"[UDP Recv Test] Received {len(samples)} samples from {addr}.")
