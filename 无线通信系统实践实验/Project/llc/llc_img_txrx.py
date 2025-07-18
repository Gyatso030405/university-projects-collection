import numpy as np
import time
import threading
import sys
import math
sys.path.append('..')

from ofdm.ofdm_tx import OfdmTx
from ofdm.ofdm_rx import OfdmRx
from llc.llc_utils import calc_crc32, check_crc32, dec2bin, bin2dec, NSEQ, SEQ_LEN, RES_LEN, CRC_LEN

class NodeALLC:
    def __init__(self, phy_type, tx_args, rx_args, packet_bit_size=100*48):
        self.ofdm_tx = OfdmTx(phy_type, tx_args)
        self.ofdm_rx = OfdmRx(phy_type, rx_args)

        self.packet_bit_size = packet_bit_size
        self.max_payload_len = packet_bit_size - SEQ_LEN - RES_LEN - CRC_LEN

        self.tx_seq_no = 0

    def send(self, payload):
        # 构造数据帧
        frame = self.pack(self.tx_seq_no, payload)
        self.ofdm_tx.put(frame)
        print(f"[NodeA] Sent SEQ={self.tx_seq_no}, payload={len(payload)} bits")

        # 简单ACK等待机制（或可加入ARQ）
        for _ in range(50):  # 最多等 50*10ms
            ack = self.ofdm_rx.get()
            if ack is None:
                time.sleep(0.01)
                continue
            ack_seq, _, ok = self.unpack(ack)
            if ok == 'ok' and ack_seq == self.tx_seq_no:
                print(f"[NodeA] Got ACK SEQ={ack_seq}")
                self.tx_seq_no = (self.tx_seq_no + 1) % NSEQ
                return True
        print("[NodeA] Timeout, no ACK")
        return False

    def pack(self, seq_no, payload):
        seq_bits = dec2bin(seq_no, SEQ_LEN)
        res_bits = np.zeros(RES_LEN, dtype=int)
        crc = calc_crc32(np.concatenate([seq_bits, res_bits, payload]))
        frame = np.concatenate([seq_bits, res_bits, payload, crc])
        return frame

    def unpack(self, frame):
        if len(frame) < SEQ_LEN + RES_LEN + CRC_LEN:
            return None, None, 'err'
        seq_bits = frame[:SEQ_LEN]
        payload = frame[SEQ_LEN+RES_LEN:-CRC_LEN]
        ok = 'ok' if check_crc32(frame) else 'err'
        return bin2dec(seq_bits), payload, ok


class NodeBLLC(threading.Thread):
    def __init__(self, phy_type, tx_args, rx_args, packet_bit_size=100*48):
        super().__init__()
        self.ofdm_tx = OfdmTx(phy_type, tx_args)
        self.ofdm_rx = OfdmRx(phy_type, rx_args)

        self.packet_bit_size = packet_bit_size
        self.max_payload_len = packet_bit_size - SEQ_LEN - RES_LEN - CRC_LEN

        self.last_seq_no = -1
        self.received_bits = []
        self.keep_running = True

    def run(self):
        while self.keep_running:
            bits = self.recv()
            if bits:
                self.received_bits.extend(bits)

    def recv(self):
        frame = self.ofdm_rx.get()
        if frame is None:
            return None

        seq, payload, ok = self.unpack(frame)
        if ok == 'ok':
            print(f"[NodeB] Got SEQ={seq}, len={len(payload)}")
            self.send_ack(seq)
            if seq != self.last_seq_no:
                self.last_seq_no = seq
                return payload
        else:
            print("[NodeB] CRC Failed")
        return None

    def send_ack(self, seq_no):
        seq_bits = dec2bin(seq_no, SEQ_LEN)
        res_bits = np.zeros(RES_LEN, dtype=int)
        crc = calc_crc32(np.concatenate([seq_bits, res_bits]))
        frame = np.concatenate([seq_bits, res_bits, crc])
        self.ofdm_tx.put(frame)
        print(f"[NodeB] Sent ACK SEQ={seq_no}")

    def unpack(self, frame):
        if len(frame) < SEQ_LEN + RES_LEN + CRC_LEN:
            return None, None, 'err'
        seq_bits = frame[:SEQ_LEN]
        payload = frame[SEQ_LEN + RES_LEN:-CRC_LEN]
        ok = 'ok' if check_crc32(frame) else 'err'
        return bin2dec(seq_bits), payload, ok

    def get_received_bits(self):
        return self.received_bits

    def stop(self):
        self.keep_running = False
