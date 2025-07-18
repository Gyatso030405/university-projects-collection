# -*- coding: utf-8 -*-
# @Author  : Zhirong Tang
# @Time    : 2022/4/14 20:22

""" Basic version of double-link LLC-layer receiver
"""

import numpy as np
import time
import threading
import sys
sys.path.append('..')

from ofdm.ofdm_tx import OfdmTx
from ofdm.ofdm_rx import OfdmRx
from llc.llc_utils import calc_crc32, check_crc32, simu_pkt_loss_delay, dec2bin, bin2dec, NSEQ


class NodeBLLC(threading.Thread):
    def __init__(self, ofdm_tx, ofdm_rx, packet_bit_size=20*48):
        """ LLC-layer receiver side
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

        # LLC-layer rx counters
        self.nrx = 0
        self.nrxok = 0

        self.keep_running = True
        self.rx_data = []

    def done(self):
        self.keep_running = False

    def recv(self, phy_type="pluto", is_dbl_link=True, arq_mode="null-ARQ"):
        while self.keep_running:
            recv_pkt = self.ofdm_rx.get()
            if True:
                if recv_pkt is None:
                    continue

                if phy_type == "socket":
                    # packet loss and delay emulator
                    is_not_dropped = simu_pkt_loss_delay()
                    if not is_not_dropped:
                        print("[NodeB] !!! {frame} dropped !!!")
                        continue

                if arq_mode == "null-ARQ":
                    # recv_pkt = self.ofdm_rx.process(recv_pkt)
                    if check_crc32(recv_pkt):
                        self.nrxok += 1
                        self.nrx += 1
                        print("[NodeB] LLCRx: pkt=ok, nrxok={}, nrx={}".format(self.nrxok, self.nrx))
                    else:
                        self.nrx += 1
                        print("[NodeB] LLCRx: pkt=false, nrxok={}, nrx={}".format(self.nrxok, self.nrx))

                    if is_dbl_link:
                        self.ack(phy_type, arq_mode)


                elif arq_mode == "stop-and-wait-ARQ":
                    # TODO: 实现stop-and-wait-ARQ protocol
                    # - 提取header处理协议流程
                    # - 提取并处理frame的数据;

                    # TODO: design unpack(), parse DATA frame, extract SEQ, PAYLOAD, and crc check result
                    rx_seq_no, payload, ok = self.unpack(recv_pkt)
                    self.nrx += 1
                    self.nrxok = self.nrxok + 1 if ok == 'ok' else self.nrxok

                    if ok == 'ok':
                        # TODO: calculate average data rate

                        # TODO: calculate packet loss rate

                        # ACK
                        self.ack(rx_seq_no, phy_type, arq_mode)

                    print("[LLCRx] RX: pkt={}, seq_no={}, nrxok={}, nrx={}, "
                          "data_rate={:.2f}kbps, pkt_loss={:.2f}%".format(ok,
                                                                          rx_seq_no,
                                                                          self.nrxok,
                                                                          self.nrx,
                                                                          rate_avg / 1000.0,
                                                                          pkt_loss))
            # except Exception as e:
            #    print(e)
            #    pass

    def ack(self, rx_seq_no, phy_type="pluto", arq_mode="null-ARQ"):
        if phy_type == "socket":
            # packet loss and delay emulator
            is_not_dropped = simu_pkt_loss_delay()
            if not is_not_dropped:
                print("[NodeB] !!! {ack} dropped !!!")
                return

        if arq_mode == "null-ARQ":
            random_bit_size = self.packet_bit_size - 32
            frame = np.random.randint(low=0, high=2, size=random_bit_size)
            # add crc32 for error detection, which is actually done by LLC layer
            crc = calc_crc32(frame)
            frame = np.concatenate((frame, crc))
            self.ofdm_tx.put(frame)

            self.ntx += 1
            print("[NodeB] LLCTx: ntx={}".format(self.ntx))
        elif arq_mode == "stop-and-wait-ARQ":
            # TODO: 实现stop-and-wait-ARQ protocol
            # - 生成ack frame
            # TODO: design pack() to generate ACK frame
            frame = self.pack(rx_seq_no)
            self.ofdm_tx.put(frame)
            self.ntx += 1
            print("[LLCRx] TX: ntx={}".format(self.ntx))
            pass

    def unpack(self, frame):
        if frame is None or len(frame) < 48:
            return 0, None, 'fail'
        ok = 'ok' if check_crc32(frame) else 'fail'
        header = frame[:16]
        payload = frame[16:-32]
        seq = bin2dec(header[:10])
        return seq, payload, ok

    def pack(self, rx_seq_no):
        header = np.concatenate((dec2bin(rx_seq_no, size=10), np.zeros(6, dtype=np.uint8)))
        crc = calc_crc32(header)
        return np.concatenate((header, crc))

    def get_received_bits(self):
        if len(self.rx_data) == 0:
            return np.array([], dtype=np.uint8)
        return np.concatenate(self.rx_data)






