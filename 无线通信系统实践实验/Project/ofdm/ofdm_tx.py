# -*- coding: utf-8 -*-

"""OFDM transmitter.

"""

# compatibility of Python 2/3
from __future__ import division
from __future__ import print_function

import struct
from multiprocessing import Manager
import threading
import numpy as np
import socket
import time
import sys
sys.path.append('..')

from ofdm.ofdm_utils import OfdmConfig
from ofdm.pluto_interface import pluto_transmitter


class OfdmTx(object):
    def __init__(self, tx_type, tx_args,
                 n=64, cp_len=16, qam_mod_size=2, pilot_pattern='custom', preamble_type='802.11', num_symbol=20,
                 verbose=False):
        """ OFDM transmitter
        :param tx_type:             'pluto', 'socket'
        :param tx_args:             including parameters below
                    tx_ipaddr:      PlutoSDR device ip address
                    tx_freq:        center frequency
                    bandwidth:      bandwidth/sample rate in Hz
                    tx_gain:        transmission gain in dB ([-90, 0]dB)
        :param n:                   the DFT size in OFDM
        :param cp_len:              length of the cyclic prefix
        :param qam_mod_size:        size of the constellation of QAM modulation
        :param pilot_pattern:       'comb', 'staggered', 'custom'
        :param preamble_type:       only '802.11' is supported
        :param num_symbol:          the number of ofdm symbols
        :param verbose:             print PHY-layer info
        """
        # Tx params
        self.tx_queue_size = 20
        self.tx_queue = Manager().Queue(self.tx_queue_size)  # thread safe
        self.tx_type = tx_type
        if self.tx_type == "pluto":
            tx_ipaddr, tx_freq, bandwidth, tx_gain = tx_args
            sdr_tx = pluto_transmitter(tx_ipaddr, tx_freq, bandwidth, tx_gain, verbose=True).pluto
            self.tx_sample_queue_watcher_thread = tx_sample_queue_watcher_thread(sdr_tx,
                                                                                 self.tx_queue,
                                                                                 self.tx_queue_size,
                                                                                 verbose=verbose)
        elif self.tx_type == "socket":
            tx_ipaddr, tx_port = tx_args
            self.tx_packet_queue_watcher_thread = tx_packet_queue_watcher_thread(tx_ipaddr, tx_port,
                                                                                 self.tx_queue,
                                                                                 self.tx_queue_size,
                                                                                 verbose=verbose)
        else:
            raise ValueError("Invalid tx type.")

        # OFDM params
        self.ofdm_config = OfdmConfig(n, cp_len, qam_mod_size, pilot_pattern)  # type: OfdmConfig
        self.preamble_type = preamble_type
        self.num_symbol = num_symbol
        self.packet_bit_size = 48 * num_symbol
        self.verbose = verbose

    def done(self):
        if self.tx_type == "pluto":
            self.tx_sample_queue_watcher_thread.done()
        elif self.tx_type == "socket":
            self.tx_packet_queue_watcher_thread.done()

    def put(self, bin_message):
        """ interface for llc-layer """
        if self.tx_type == "socket":
            # put modulated samples into tx_queue for socket
            self.tx_queue.put(self.process(bin_message))
        elif self.tx_type == "pluto":
            # put modulated samples into tx_queue for pluto
            # TODO
            pass

    def process(self, bin_message, is_with_preamble=True):
        """ Calculate the time-domain samples to be transmitted
        :param bin_message:         (numpy.array) binary message array
        :param is_with_preamble:    (boolean) whether to use the preamble
        :return: (numpy.array) baseband time-domain samples to be transmitted
        """
        # 1. 检查输入的二进制消息长度是否符合要求
        if bin_message.size > self.packet_bit_size:
            print("Warning: input binary message is too long, truncating...")
            bin_message = bin_message[:self.packet_bit_size]
        elif bin_message.size < self.packet_bit_size:
            # 如果输入的二进制消息长度不足，用0填充
            pad_len = self.packet_bit_size - bin_message.size
            bin_message = np.concatenate((bin_message, np.zeros(pad_len, dtype=bin_message.dtype)))
        
        # 2. 将二进制消息调制为复数符号
        # 计算每个OFDM符号需要的数据子载波数量
        data_sc_num = self.ofdm_config.data_sc_num
        # 计算需要多少个OFDM符号来传输所有数据
        ofdm_sym_num = self.num_symbol
        
        # 3. 创建频域符号矩阵 (n x ofdm_sym_num)
        freq_symbols = np.zeros((self.ofdm_config.n, ofdm_sym_num), dtype=complex)
        
        # 4. 调制二进制消息为QAM符号
        # 每个数据子载波调制一个QAM符号
        qam_symbols = self.ofdm_config.qam_mod.modulate(bin_message)
        
        # 5. 将QAM符号映射到频域符号矩阵的数据子载波位置
        # 获取数据子载波和导频子载波的索引
        pilot_sc_index = self.ofdm_config.pilot_sc_index
        data_sc_index = self.ofdm_config.data_sc_index
        
        # 将QAM符号放入数据子载波位置
        for i in range(ofdm_sym_num):
            # 获取当前OFDM符号的数据子载波索引
            _, curr_data_sc_index = self.ofdm_config.ofdm_pilot.get_pilot_and_data_index_at_symbol(i)
            # 计算当前OFDM符号需要的QAM符号数量
            curr_data_sc_num = curr_data_sc_index.size
            # 计算当前OFDM符号对应的QAM符号起始索引
            start_idx = i * curr_data_sc_num
            end_idx = start_idx + curr_data_sc_num
            # 如果索引超出了QAM符号的范围，则截断
            if end_idx > qam_symbols.size:
                end_idx = qam_symbols.size
            # 将QAM符号放入数据子载波位置
            if start_idx < qam_symbols.size:
                freq_symbols[curr_data_sc_index, i] = qam_symbols[start_idx:end_idx]
        
        # 6. 在导频子载波位置插入导频符号
        # 导频符号通常使用BPSK调制的已知序列
        pilot_symbols = np.ones(pilot_sc_index.size, dtype=complex)  # 使用全1作为导频符号
        for i in range(ofdm_sym_num):
            # 获取当前OFDM符号的导频子载波索引
            curr_pilot_sc_index, _ = self.ofdm_config.ofdm_pilot.get_pilot_and_data_index_at_symbol(i)
            # 将导频符号放入导频子载波位置
            freq_symbols[curr_pilot_sc_index, i] = pilot_symbols
        
        # 7. 对每个OFDM符号进行IFFT，得到时域符号
        time_symbols = np.zeros((self.ofdm_config.n, ofdm_sym_num), dtype=complex)
        for i in range(ofdm_sym_num):
            time_symbols[:, i] = np.fft.ifft(freq_symbols[:, i], n=self.ofdm_config.n)
        
        # 8. 添加循环前缀
        # 循环前缀是时域符号末尾的一部分复制到符号开头
        cp_len = self.ofdm_config.cp_len
        time_symbols_with_cp = np.zeros((self.ofdm_config.n + cp_len, ofdm_sym_num), dtype=complex)
        for i in range(ofdm_sym_num):
            # 复制时域符号末尾的一部分作为循环前缀
            time_symbols_with_cp[:cp_len, i] = time_symbols[-cp_len:, i]
            # 复制整个时域符号
            time_symbols_with_cp[cp_len:, i] = time_symbols[:, i]
        
        # 9. 将所有OFDM符号串联成一个序列
        time_samples = time_symbols_with_cp.flatten('F')  # 按列展平
        
        # 10. 如果需要添加前导码，则在序列开头添加STS和LTS
        if is_with_preamble:
            # 添加STS和LTS前导码
            preamble = self.ofdm_config.preamble
            time_samples = np.concatenate((preamble, time_samples))
        
        return time_samples


class tx_sample_queue_watcher_thread(threading.Thread):
    """ TX Sample Queue Monitor for pluto
    """
    # TODO: implement the thread for pluto


class tx_packet_queue_watcher_thread(threading.Thread):
    """ TX UDP Packet Queue Monitor for socket
    """
    def __init__(self, tx_ipaddr, tx_port, tx_queue, tx_queue_size, verbose=False):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tx_ipaddr = tx_ipaddr
        self.tx_port = tx_port
        self.ntx = 0
        self.tx_queue = tx_queue
        self.tx_queue_size = tx_queue_size
        self.verbose = verbose
        self.keep_running = True
        self.start()


    def done(self):
        self.keep_running = False

    def run(self):
        while self.keep_running:
            try:
                if self.tx_queue.full():
                    self.tx_queue.get()
                if not self.tx_queue.empty():
                    # get the complex samples
                    data_samples = self.tx_queue.get()
                    data_bytes = data_samples.tobytes()
                    self.sock.sendto(data_bytes, (self.tx_ipaddr, self.tx_port))
                    if self.verbose:
                        self.ntx += 1
                        print("[SocketTx] TX: ntx={}".format(self.ntx))
            except:
                self.sock.close()
                break
