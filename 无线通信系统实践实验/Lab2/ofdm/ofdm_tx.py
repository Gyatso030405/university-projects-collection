# -*- coding: utf-8 -*-

"""OFDM transmitter.

"""

# compatibility of Python 2/3
from __future__ import division
from __future__ import print_function
from multiprocessing import Manager
import threading
import binascii
import numpy as np
import time

from ofdm.ofdm_utils import OfdmConfig


class OfdmTx(object):
    def __init__(self, tx_args, tx_freq, bandwidth, tx_gain,
                 n=64, cp_len=16, qam_mod_size=2, pilot_pattern='custom', preamble_type='802.11', num_symbol=20,
                 verbose=False):
        """ OFDM transmitter
        :param tx_args:             PlutoSDR device ip address
        :param tx_freq:             center frequency
        :param bandwidth:           bandwidth/sample rate in Hz
        :param tx_gain:             transmission gain in dB ([-90, 0]dB)
        :param n:                   the DFT size in OFDM
        :param cp_len:              length of the cyclic prefix
        :param qam_mod_size:        size of the constellation of QAM modulation
        :param pilot_pattern:       'comb', 'staggered', 'custom'
        :param preamble_type:       only '802.11' is supported
        :param num_symbol:          the number of ofdm symbols
        :param verbose:             print PHY-layer info
        """
        self.sdr_tx = None #pluto_transmitter(tx_args, tx_freq, bandwidth, tx_gain, verbose=True).pluto

        self.ofdm_config = OfdmConfig(n, cp_len, qam_mod_size, pilot_pattern)  # type: OfdmConfig
        self.preamble_type = preamble_type
        self.num_symbol = num_symbol
        self.packet_bit_size = 48 * num_symbol
        self.verbose = verbose


        self.ntx = 0

    def dec2bin(self, decimal, bit_size=32):
        binary = np.array([], dtype=int)
        for index in range(0, bit_size):
            temp = decimal & 0x1
            decimal >>= 1
            binary = np.append(binary, temp)
        return binary


    def process(self, bin_message, is_with_preamble=True):
        """Calculate the time-domain samples to be transmitted
        :param bin_message:         (numpy.array) binary message array
        :param is_with_preamble:    (boolean) whether to use the preamble
        :return: (numpy.array) baseband time-domain samples to be transmitted
        """
        encoded = bin_message
        # zero-padding the encoded to fill a multiple of OFDM symbols
        encoded = np.concatenate((encoded, np.zeros(
            (self.ofdm_config.n_cbps - encoded.size % self.ofdm_config.n_cbps) % self.ofdm_config.n_cbps, dtype=int)))
        assert encoded.size % self.ofdm_config.n_cbps == 0

        """ QAM Modulation """
        modulated = self.ofdm_config.qam_mod.modulate(encoded) / self.ofdm_config.qam_mod.qam_max_axis
        modulated_len = modulated.size


        """ frequency domain: fill in data and pilots """
        ofdm_sym_num = self.ofdm_config.how_many_symbols(modulated_len)  # the OFDM symbol number that can hold the data
        all_sc = np.zeros((self.ofdm_config.n, ofdm_sym_num), dtype=complex)
        pilot_index_array, data_index_array = self.ofdm_config.ofdm_pilot.get_index_array_at_symbol(
            np.array(range(0, ofdm_sym_num)))
        all_sc[pilot_index_array] = self.ofdm_config.training_signal_freq[pilot_index_array[0]]
        all_sc[data_index_array] = np.concatenate(
            (modulated, np.zeros(len(data_index_array[0]) - modulated_len, dtype=complex)))

        """ IFFT: freq domain to time domain """
        time_symbols = np.fft.ifft(all_sc, n=self.ofdm_config.n, axis=0)

        """ cyclic prefix (CP) """
        time_symbols_cp = np.concatenate((time_symbols[-self.ofdm_config.cp_len:, :], time_symbols), axis=0)
        # serialization
        ofdm_symbols = np.reshape(time_symbols_cp, (self.ofdm_config.sym_len * ofdm_sym_num,), order='F')

        """ packet format: preamble + OFDM symbols
        10 STS + 2 LTS as the preamble
        """
        if is_with_preamble:
            tx_packet = np.concatenate((self.ofdm_config.preamble, ofdm_symbols))
        else:
            tx_packet = ofdm_symbols

        assert tx_packet.size % self.ofdm_config.sym_len == 0

        return tx_packet



