# -*- coding: utf-8 -*-
# @Author  : Zhirong Tang
# @Time    : 2022/4/14 20:22

""" Basic version of LLC-layer transmitter
"""

import numpy as np
import time
import threading
import sys
import math
#import test_read_save_imag as img
sys.path.append('..')

from ofdm.ofdm_tx import OfdmTx
from ofdm.ofdm_rx import OfdmRx
from llc.llc_utils import calc_crc32, check_crc32, dec2bin, bin2dec, NSEQ


class NodeALLC(threading.Thread):
    def __init__(self, ofdm_tx, ofdm_rx, packet_bit_size=20*48):
        """ LLC-layer transmitter side
        :param ofdm_tx:         physical-layer ofdm transmitter instance
        :param ofdm_rx:         physical-layer ofdm receiver instance
        :param packet_bit_size: # of bits within a frame
        """
        threading.Thread.__init__(self)
        
        # PHY-layer parameters
        self.ofdm_tx = ofdm_tx  # type: OfdmTx
        self.ofdm_rx = ofdm_rx  # type: OfdmRx

        # LLC-layer frame parameters
        self.packet_bit_size = packet_bit_size
        self.crc_bit_size = 32

        # LLC-layer tx parameters
        self.ntx = 0
        self.tx_seq_no = 0


        # LLC-layer rx counters
        self.nrx = 0
        self.nrxok = 0
        self.ack = 0
        self.rtt = 0
        self.pkt_loss = 100
        self.avg_rtt = 0
        self.tot_rtt = 0



        self.keep_running = True

    def done(self):
        self.keep_running = False

    def run(self):
        while self.keep_running:
            self.recv(arq_mode="stop-and-wait-ARQ")

    def send(self, is_dbl_link=False, arq_mode="null-ARQ", pause=0.5):
        if arq_mode == "null-ARQ":
            if is_dbl_link:
                # start thread to receive ACK
                self.start()
            while self.keep_running:
                random_bit_size = self.packet_bit_size - self.crc_bit_size
                frame = np.random.randint(low=0, high=2, size=random_bit_size)
                # add crc32 for error detection, which is actually done by LLC layer
                crc = calc_crc32(frame)
                frame = np.concatenate((frame, crc))
                self.ofdm_tx.put(frame)

                self.ntx += 1
                print("[NodeA] LLCTx: ntx={}".format(self.ntx))
                time.sleep(pause)

        elif arq_mode == "stop-and-wait-ARQ":
            # TODO: 实现stop-and-wait-ARQ protocol
            # - 提取数据, 生成协议的header
            if is_dbl_link:
                self.start()
            while self.keep_running:
                # TODO: design stop-and-wait-ARQ protocol, including DATA frame, extract SEQ, PAYLOAD, and crc check result, pause can be used as timeout
                frame = self.pack(tx_seq_no, payload)
                self.ofdm_tx.put(frame)

                print("[LLCTx] TX: seq_no={}".format(tx_seq_no))
                time.sleep(pause)
                pass

    def recv(self, arq_mode):
        frame = self.ofdm_rx.get()
        if frame is None:
            return

        if arq_mode == "null-ARQ":
            if check_crc32(frame):
                self.nrxok += 1
                self.nrx += 1
                print("[NodeA] LLCRx: pkt=ok, nrxok={}, nrx={}".format(self.nrxok, self.nrx))
            else:
                self.nrx += 1
                print("[NodeA] LLCRX: pkt=false, nrxok={}, nrx={}".format(self.nrxok, self.nrx))

        if arq_mode == "stop-and-wait-ARQ":
            # TODO: 实现stop-and-wait-ARQ protocol
            # - 提取frame的其他字段, 处理协议流程; 处理数据

            # TODO: design unpack(), parse DATA frame, extract SEQ, PAYLOAD, and crc check result
            ack_seq_no, _, ok = self.unpack(frame)
            self.nrx += 1
            self.nrxok = self.nrxok + 1 if ok == 'ok' else self.nrxok
            if ok == 'ok':
                # TODO: calculate packet loss rate

                # TODO: calculate round trip time (RTT)

               print("[LLCTx] RX: pkt={}, seq_no={}, nrxok={}, nrx={}, "
                      "rtt={:.2f}ms, avg_rtt={:.2f}ms, pkt_loss={:.2f}%".format(ok,
                                                                                ack_seq_no,
                                                                                self.nrxok,
                                                                                self.nrx,
                                                                                self.rtt,
                                                                                self.avg_rtt,
                                                                                self.pkt_loss))

    def pack(self, tx_seq_no, payload):
        header = np.concatenate(
            (dec2bin(tx_seq_no, size=10), np.zeros(6, dtype=np.uint8)))  # 10-bit seq + 6-bit reserved
        frame = np.concatenate((header, payload))
        crc = calc_crc32(frame)
        return np.concatenate((frame, crc))

    def unpack(self, frame):
        if frame is None or len(frame) < self.crc_bit_size + 16:
            return 0, None, 'fail'
        ok = 'ok' if check_crc32(frame) else 'fail'
        header = frame[:16]
        ack_seq_no = bin2dec(header[:10])
        return ack_seq_no, None, ok

