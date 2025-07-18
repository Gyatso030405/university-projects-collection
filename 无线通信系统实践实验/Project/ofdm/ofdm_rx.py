# -*- coding: utf-8 -*-
# @Author  : ZhirongTang
# @Time    : 2021/12/11 11:18 PM


import math
import numpy as np
import threading
from multiprocessing import Manager
from scipy import optimize as op
import socket
import struct
import random
import time
import sys
sys.path.append('..')

from ofdm.ofdm_utils import OfdmConfig
from ofdm.pluto_interface import pluto_receiver


class OfdmRx(threading.Thread):
    def __init__(self, rx_type, rx_args,
                 n=64, cp_len=16, qam_mod_size=2, pilot_pattern='custom', preamble_type='802.11', num_symbol=20,
                 verbose=False):
        """ OFDM receiver
        :param rx_type:                 'pluto', 'socket'
        :param rx_args:                 including parameters below
                    rx_args:            PlutoSDR device ip address
                    rx_freq:            center frequency
                    bandwidth:          bandwidth/sample rate in Hz
                    rx_gain:            reception gain in dB ([0, 75]dB)
                    rx_buffer_size:     reception buffer size of PlutoSDR device
                    gain_control_mode:  'manual', 'fast_attack', 'slow_attack'
        :param n:                       the DFT size in OFDM
        :param cp_len:                  length of the cyclic prefix
        :param qam_mod_size:            size of the constellation of QAM modulation
        :param pilot_pattern:           'comb', 'staggered', 'custom'
        :param preamble_type:           only '802.11' is supported
        :param num_symbol:              the number of ofdm symbols
        :param verbose:                 print PHY-layer info
        """
        # Rx params
        threading.Thread.__init__(self)
        self.rx_sample_queue_size = 20
        self.rx_sample_queue = Manager().Queue(self.rx_sample_queue_size)  # raw samples from PlutoSDR device

        self.rx_packet_queue_size = 20
        self.rx_packet_queue = Manager().Queue(self.rx_packet_queue_size)  # packet bits

        self.rx_type = rx_type
        if self.rx_type == "pluto":
            rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size, gain_control_mode = rx_args
            sdr_rx = pluto_receiver(rx_args, rx_freq, bandwidth, rx_gain, rx_buffer_size,
                                         gain_control_mode, verbose=True).pluto
            self.rx_sample_queue_watcher_thread = rx_sample_queue_watcher_thread(sdr_rx,
                                                                                 self.rx_sample_queue,
                                                                                 self.rx_sample_queue_size,
                                                                                 verbose=verbose)
        elif self.rx_type == "socket":
            rx_ipaddr, rx_port = rx_args
            self.rx_packet_queue_watcher_thread = rx_packet_queue_watcher_thread(rx_ipaddr, rx_port,
                                                                                 self.rx_sample_queue,
                                                                                 self.rx_sample_queue_size,
                                                                                 verbose=verbose)
        else:
            raise ValueError("Invalid rx type.")

        # OFDM params
        self.ofdm_config = OfdmConfig(n, cp_len, qam_mod_size, pilot_pattern)  # type: OfdmConfig
        self.preamble_type = preamble_type
        self.num_symbol = num_symbol
        self.prev_samples = np.array([])
        self.packet_length = self.ofdm_config.preamble_sts_len + self.ofdm_config.preamble_lts_len + \
                             self.num_symbol * self.ofdm_config.sym_len

        self.verbose = verbose
        self.nrx = 0
        self.nrxok = 0

        self.keep_running = True
        self.start()

    def done(self):
        self.keep_running = False
        if self.rx_type == "pluto":
            self.rx_sample_queue_watcher_thread.done()
        elif self.rx_type == "socket":
            self.rx_packet_queue_watcher_thread.done()

    def run(self):
        """ thread for sample process
        """
        if self.rx_type == "pluto":
            while self.keep_running:
                self.process()
        elif self.rx_type == "socket":
            while self.keep_running:
                #self.num_symbol = 20
                self.process()

    def get(self):
        """ interface for upper layers
        """
        return self.rx_packet_queue.get() if not self.rx_packet_queue.empty() else None

    def process(self):
        """ Demodulate received samples and put packet into rx_packet_queue """
        print("[DEBUG] Entered process()")
        # 如果接收队列是空的，就不处理
        if self.rx_sample_queue.empty():
            print("[DEBUG] rx_sample_queue is empty")
            time.sleep(5)
            return

        print("[DEBUG] rx_sample_queue is NOT empty")
        #'''
        ##实验1，2，3的代码  step1,2,3
        # Step 1: 从队列取出一段复数采样数据（baseband）
        samples = self.rx_sample_queue.get()
        samples = np.concatenate((self.prev_samples, samples))  # 拼上前一次剩下的
        self.prev_samples = np.array([])
        print("finsh step1")

        # Step 2: 帧同步（时域相关匹配 LTS）
        lts_time = self.ofdm_config.preamble_lts
        corr = np.abs(np.correlate(samples, lts_time[::-1].conj(), mode='valid'))
        
        # 寻找所有可能的峰值
        peak_threshold = 0.7 * np.max(corr)
        peaks = np.where(corr > peak_threshold)[0]
        
        if len(peaks) == 0:
            print("[DEBUG] Frame sync failed: no peaks found")
            self.prev_samples = samples
            return
            
        # 选择第一个有效的峰值
        valid_peak = None
        for peak in peaks:
            potential_frame_start = peak - (self.ofdm_config.preamble_lts_len - 1) - self.ofdm_config.preamble_sts_len
            if potential_frame_start >= 0 and potential_frame_start + self.packet_length <= len(samples):
                valid_peak = peak
                break
                
        if valid_peak is None:
            print("[DEBUG] Frame sync failed: no valid frame position found")
            self.prev_samples = samples
            return
            
        peak_index = valid_peak
        print("finsh step2")
        print("[DEBUG] peak_index =", peak_index)
        print("[DEBUG] preamble_lts_len =", self.ofdm_config.preamble_lts_len)
        print("[DEBUG] preamble_sts_len =", self.ofdm_config.preamble_sts_len)
        print("[DEBUG] total packet_length =", self.packet_length)
        print("[DEBUG] total samples length =", len(samples))


        # Step 3: 推断帧起始位置（包括 STS 和 LTS）
        frame_start = peak_index - (self.ofdm_config.preamble_lts_len - 1) - self.ofdm_config.preamble_sts_len
        print("[DEBUG] frame_start =", frame_start)
        if frame_start < 0 or frame_start + self.packet_length > len(samples):
            # 如果帧不完整，就保留数据
            self.prev_samples = samples
            return
        print("[DEBUG] frame_start =", frame_start)

        frame = samples[frame_start:frame_start + self.packet_length]
        print("finsh step3")
        '''
        #实验4的代码  step1,2,3
        # Step 1: 从队列取出采样数据并检查长度
        if self.rx_sample_queue.empty():
            print("[DEBUG] rx_sample_queue is empty")
            return

        samples = self.rx_sample_queue.get()
        samples = np.concatenate((self.prev_samples, samples))
        
        # 检查是否有足够的采样点进行帧检测
        min_required_samples = self.packet_length * 3  # 增加到三倍帧长以提高检测可靠性
        if len(samples) < min_required_samples:
            print(f"[DEBUG] Not enough samples: {len(samples)} < {min_required_samples}")
            self.prev_samples = samples
            return
        print("finsh step1")

        # Step 2: 帧同步 - 使用双重相关检测
        lts_time = self.ofdm_config.preamble_lts
        sts_time = self.ofdm_config.preamble_sts
        
        # LTS相关
        lts_corr = np.abs(np.correlate(samples, lts_time[::-1].conj(), mode='valid'))
        # STS相关
        sts_corr = np.abs(np.correlate(samples, sts_time[::-1].conj(), mode='valid'))
        
        # 计算噪声底和动态阈值
        noise_floor_lts = np.median(lts_corr)  # 使用中值估计噪声底，更鲁棒
        noise_floor_sts = np.median(sts_corr)
        
        # 动态阈值，基于信噪比，降低阈值要求以提高检测灵敏度
        peak_threshold_lts = max(0.3 * np.max(lts_corr), 2 * noise_floor_lts)
        peak_threshold_sts = max(0.3 * np.max(sts_corr), 2 * noise_floor_sts)
        
        # 寻找LTS和STS的峰值，按照相关值大小排序
        lts_peaks = np.where(lts_corr > peak_threshold_lts)[0]
        sts_peaks = np.where(sts_corr > peak_threshold_sts)[0]
        
        if len(lts_peaks) == 0:
            print("[DEBUG] 未发现有效的LTS相关峰")
            self.prev_samples = samples[-self.packet_length:]
            return
            
        # 按相关值大小对峰值进行排序
        lts_peaks = lts_peaks[np.argsort(lts_corr[lts_peaks])[::-1]]
        if len(sts_peaks) > 0:
            sts_peaks = sts_peaks[np.argsort(sts_corr[sts_peaks])[::-1]]
        
        # 选择最强的LTS峰值
        lts_peak_index = lts_peaks[0]
        lts_peak_value = lts_corr[lts_peak_index]
        lts_peak_snr = 10 * np.log10(lts_peak_value / noise_floor_lts)
        
        # 验证LTS峰值的信噪比
        if lts_peak_snr < 6:  # 降低SNR要求到6dB
            print(f"[DEBUG] LTS Peak SNR too low: {lts_peak_snr:.1f}dB")
            self.prev_samples = samples[-self.packet_length:]
            return
            
        # 如果找不到STS峰值，仍然尝试使用LTS峰值进行同步
        if len(sts_peaks) == 0:
            print("[DEBUG] 未发现STS相关峰，仅使用LTS进行同步")
            sts_peak_index = lts_peak_index - self.ofdm_config.preamble_lts_len
            sts_peak_snr = 0
        else:
            # 选择最强的STS峰值
            sts_peak_index = sts_peaks[0]
            sts_peak_value = sts_corr[sts_peak_index]
            sts_peak_snr = 10 * np.log10(sts_peak_value / noise_floor_sts)
            
        # 使用LTS峰值作为主要参考点
        peak_index = lts_peak_index
        print("finish step2")
        print("[DEBUG] peak_index =", peak_index)
        print("[DEBUG] preamble_lts_len =", self.ofdm_config.preamble_lts_len)
        print("[DEBUG] preamble_sts_len =", self.ofdm_config.preamble_sts_len)
        print("[DEBUG] total packet_length =", self.packet_length)
        print("[DEBUG] total samples length =", len(samples))

        # Step 3: 计算并验证帧起始位置
        # 使用LTS和STS峰值的位置关系来验证帧同步
        expected_sts_peak = lts_peak_index - self.ofdm_config.preamble_lts_len
        sts_peak_tolerance = 20  # 增加误差容忍范围
        
        # 在STS峰值列表中查找最接近预期位置的峰值
        if len(sts_peaks) > 0:
            # 计算每个STS峰值到预期位置的距离
            peak_distances = np.abs(sts_peaks - expected_sts_peak)
            closest_peak_idx = np.argmin(peak_distances)
            
            if peak_distances[closest_peak_idx] < sts_peak_tolerance:
                # 使用最接近预期位置的STS峰值
                sts_peak = sts_peaks[closest_peak_idx]
                frame_start = sts_peak
                print(f"[DEBUG]发现有效 STS 峰值位于 {sts_peak}, 与预期的距离={peak_distances[closest_peak_idx]}")
            else:
                # 如果没有足够接近的STS峰值，使用LTS位置估计帧起始
                frame_start = lts_peak_index - (self.ofdm_config.preamble_lts_len + self.ofdm_config.preamble_sts_len)
                print(f"[DEBUG] Using LTS-based frame start estimation: {frame_start}")
        else:
            # 如果完全没有STS峰值，使用LTS位置估计帧起始
            frame_start = lts_peak_index - (self.ofdm_config.preamble_lts_len + self.ofdm_config.preamble_sts_len)
            print(f"[DEBUG] No STS peaks found, using LTS-based frame start: {frame_start}")
        
        # 验证帧起始位置的有效性并进行修正
        if frame_start < 0:
            print(f"[DEBUG] Negative frame_start={frame_start}, adjusting...")
            # 保存更多样本等待下次处理
            self.prev_samples = samples
            return
        
        # 确保有足够的采样点包含完整帧
        if frame_start + self.packet_length > len(samples):
            print(f"[DEBUG] Incomplete frame at {frame_start}, need more samples")
            # 只保留可能包含帧起始的部分
            self.prev_samples = samples[max(0, frame_start-self.ofdm_config.preamble_sts_len):]
            return
        
        # 提取帧数据
        frame = samples[frame_start:frame_start + self.packet_length]
        
        # 确保帧长度足够
        if len(frame) < self.packet_length:
            print(f"[DEBUG] Frame too short: {len(frame)} < {self.packet_length}")
            self.prev_samples = samples[frame_start:]
            return
            
        # 计算帧的能量分布
        segment_size = self.packet_length // 4  # 确保每段大小相等
        frame_segments = [frame[i:i+segment_size] for i in range(0, self.packet_length, segment_size)]
        segment_energies = [np.mean(np.abs(seg) ** 2) for seg in frame_segments if len(seg) > 0]
        
        # 验证能量分布是否合理（前半部分应该有更高的能量，因为包含前导码）
        if len(segment_energies) < 2:  # 确保至少有两段
            print("[DEBUG] Not enough segments for energy validation")
            self.prev_samples = samples[frame_start + self.packet_length:]
            return
        
        # 验证前两段的能量是否高于最后一段
        if segment_energies[0] < segment_energies[-1] or segment_energies[1] < segment_energies[-1]:
            print("[DEBUG] Suspicious energy distribution in frame")
            self.prev_samples = samples[frame_start + self.packet_length:]
            return
        
        # 计算帧SNR
        # 使用多个窗口估计噪声底
        noise_windows = [
            samples[max(0, frame_start-200):max(0, frame_start-100)],  # 帧前较远的窗口
            samples[max(0, frame_start-100):frame_start],  # 帧前较近的窗口
            samples[min(len(samples), frame_start+self.packet_length):min(len(samples), frame_start+self.packet_length+100)]  # 帧后的窗口
        ]
        noise_energies = [np.mean(np.abs(w) ** 2) for w in noise_windows if len(w) > 0]
        if not noise_energies:  # 如果没有有效的噪声窗口
            noise_energy = min(segment_energies) / 5  # 使用最小段能量的1/5作为噪声估计
        else:
            noise_energy = np.median(noise_energies)  # 使用中值作为更稳健的估计
        
        # 使用有效的段计算SNR
        valid_segments = min(2, len(segment_energies))  # 确保不会越界
        frame_snr = 10 * np.log10(np.mean(segment_energies[:valid_segments]) / noise_energy)  # 使用前两段（包含前导码）的能量计算SNR
        
        if frame_snr < 3:  # 降低SNR要求到3dB
            print(f"[DEBUG] Frame SNR too low: {frame_snr:.1f}dB")
            self.prev_samples = samples[frame_start + self.packet_length:]
            return
        
        # 保存剩余样本用于下次处理
        remaining_samples = samples[frame_start + self.packet_length:]
        if len(remaining_samples) > self.packet_length:
            self.prev_samples = remaining_samples[-self.packet_length:]
        else:
            self.prev_samples = remaining_samples
            
        print(f"[DEBUG] Frame found: start={frame_start}, SNR={frame_snr:.1f}dB")
        '''


        # Step 4: 使用LTS进行简化的信道估计
        lts_start = self.ofdm_config.preamble_sts_len
        lts_end = lts_start + self.ofdm_config.preamble_lts_len
        lts_samples = frame[lts_start:lts_end]
        
        # 去除CP并进行FFT得到频域LTS
        lts_freq = np.fft.fft(lts_samples[self.ofdm_config.cp_len:], n=self.ofdm_config.n)
        
        # 使用已知的LTS频域符号进行信道估计
        known_lts_freq = np.fft.fft(self.ofdm_config.preamble_lts[self.ofdm_config.cp_len:], n=self.ofdm_config.n)
        
        # 添加防护，避免除以零
        epsilon = 1e-10
        known_lts_freq = np.where(np.abs(known_lts_freq) > epsilon, known_lts_freq, epsilon)
        
        # 计算初始信道估计
        channel_estimate = lts_freq / known_lts_freq
        
        # 简单的频域平滑
        smooth_window = 3
        smooth_channel = np.zeros_like(channel_estimate, dtype=np.complex128)
        for i in range(len(channel_estimate)):
            start_idx = max(0, i - smooth_window//2)
            end_idx = min(len(channel_estimate), i + smooth_window//2 + 1)
            smooth_channel[i] = np.mean(channel_estimate[start_idx:end_idx])
        channel_estimate = smooth_channel
        
        # 计算平均信道功率
        channel_power = np.abs(channel_estimate) ** 2
        avg_power = np.mean(channel_power)
        
        print(f"[DEBUG] Channel estimation complete: avg_power={avg_power:.2e}")



        # Step 5: 提取数据部分
        data_start = self.ofdm_config.preamble_sts_len + self.ofdm_config.preamble_lts_len
        data_samples = frame[data_start:]

        sym_len = self.ofdm_config.n + self.ofdm_config.cp_len
        num_symbols = self.num_symbol

        if len(data_samples) < num_symbols * sym_len:
            self.prev_samples = samples
            return
        print("finsh step5")

        # Step 6: reshape成多个OFDM符号并去除循环前缀
        symbols = data_samples[:num_symbols * sym_len].reshape((num_symbols, sym_len))
        no_cp_symbols = symbols[:, self.ofdm_config.cp_len:]  # shape: (num_symbols, n)
        print("finsh step6")

        # Step 7: 对每个符号做FFT得到频域符号
        freq_symbols = np.fft.fft(no_cp_symbols, n=self.ofdm_config.n, axis=1)
        print("Finsh Step7")
        
        # Step 8: 信道均衡
        for i in range(num_symbols):
            freq_symbols[i] = freq_symbols[i] / channel_estimate
        print("Finsh step8")

        # Step 9: 提取数据子载波和导频子载波
        qam_symbols = []
        for i in range(num_symbols):
            pilot_idx, data_idx = self.ofdm_config.ofdm_pilot.get_pilot_and_data_index_at_symbol(i)
            # 获取导频符号用于相位校正（这里可以进一步改进）
            pilot_symbols = freq_symbols[i, pilot_idx]
            # 获取数据符号
            qam_symbols.extend(freq_symbols[i, data_idx])
        qam_symbols = np.array(qam_symbols)
        print("Finsh Step9")

        # Step 10: 简化的QAM解调
        # 计算平均符号功率
        avg_power = np.mean(np.abs(qam_symbols) ** 2)
        
        # 归一化QAM符号
        qam_symbols_norm = qam_symbols / np.sqrt(avg_power)
        
        # 固定判决门限
        threshold = 0.0
        
        bits = []
        for s in qam_symbols_norm:
            # 提取实部和虚部
            real = s.real
            imag = s.imag
            
            # QPSK解调
            bits.extend([1 if real > threshold else 0,
                        1 if imag > threshold else 0])
        
        print(f"[DEBUG] QAM demodulation complete: {len(bits)} bits recovered")
        
        # 确保比特长度正确
        target_len = self.num_symbol * self.ofdm_config.data_sc_num * int(np.log2(self.ofdm_config.qam_mod.m))
        if len(bits) > target_len:
            bits = bits[:target_len]
        elif len(bits) < target_len:
            print(f"[DEBUG] Warning: Not enough bits decoded: {len(bits)} < {target_len}")
            # 补充缺失的比特，使用最后一个有效比特的值
            pad_value = bits[-1] if len(bits) > 0 else 0
            bits = np.pad(bits, (0, target_len - len(bits)), 'constant', constant_values=pad_value)
        
        # 转换为numpy数组
        bits = np.array(bits, dtype=np.uint8)

        # Step 11: 放入packet queue
        if self.rx_packet_queue.full():
            self.rx_packet_queue.get()
        self.rx_packet_queue.put(bits)

        if self.verbose:
            self.nrx += 1
            print("[OfdmRx] 解调成功，第 {} 帧，bit数: {}".format(self.nrx, len(bits)))

        return bits


class rx_sample_queue_watcher_thread(threading.Thread):
    """ Rx Queue Monitor for pluto
    """
    # TODO: implement the thread for pluto
    pass


class rx_packet_queue_watcher_thread(threading.Thread):
    """ Rx Queue Monitor for socket
    """
    def __init__(self, rx_ipaddr, rx_port, rx_queue, rx_queue_size, verbose=False):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.keep_running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx_ipaddr = rx_ipaddr
        self.rx_port = rx_port
        self.sock.bind((self.rx_ipaddr, self.rx_port))
        self.rx_queue = rx_queue
        self.rx_queue_size = rx_queue_size
        self.verbose = verbose
        self.start()


    def done(self):
        self.keep_running = False

    def run(self):
        while self.keep_running:
            try:
                """Put packet to FIFO queue """
                if self.rx_queue.full():
                    self.rx_queue.get()
                # receive bytes from socket
                data_bytes = self.sock.recvfrom(65507)[0]
                #deserialize the complex samples
                print("[DEBUG][NodeB] Received {} bytes".format(len(data_bytes)))
                received_samples = np.frombuffer(data_bytes, dtype=np.complex128)
                self.rx_queue.put_nowait(received_samples)
                if self.verbose:
                    # can be used to check if rx queue is processed timely
                    print("[SocketRxQueue] RX queue size: {}".format(self.rx_queue.qsize()))
            except Exception as e:
                print(e)
                self.sock.close()
                break
