# -*- coding: utf-8 -*-

"""utils of reference signals generation: training sequence and pilots.

"""

# compatibility
from __future__ import division
from __future__ import print_function
from builtins import object

import numpy as np
from gray_qammod import GrayQamMod



class OfdmConfig(object):
    """OFDM parameters configuration

    Attributes:
        n: the DFT size in OFDM
        cp_len: length of the cyclic prefix
        f_s: sampling frequency
        qam_mod_size: size of the constellation of QAM modulation
        pilot_pattern: 'comb', 'staggered'
    """
    def __init__(self, n, cp_len, qam_mod_size, pilot_pattern, pilot_num=None):
        assert (np.log2(n) % 1) < 1e-10
        self.n = n
        self.cp_len = cp_len
        self.sym_len = self.n + self.cp_len
        self.qam_mod = GrayQamMod(qam_mod_size)
        training_signal_freq = np.array([0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1,
                                         1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0,
                                         0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1,
                                         1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1], dtype=complex)
        training_sc_index = np.where(training_signal_freq != 0)[0]
        pilot_sc_index = np.array([7, 21, 43, 57])
        assert pilot_pattern in ['comb', 'staggered', 'custom']
        self.pilot_pattern = pilot_pattern
        if pilot_pattern == 'custom':
            assert pilot_num is None and training_signal_freq is not None and training_sc_index is not None and \
                   pilot_sc_index is not None
        if pilot_num:
            self.pilot_num = pilot_num
        else:
            self.pilot_num = pilot_sc_index.size

        self.training_signal_freq, self.training_sc_index, self.ofdm_pilot = \
            self._generate_freq_ref_signal(self.n, self.pilot_pattern, self.pilot_num,
                                           training_signal_freq, training_sc_index, pilot_sc_index)
        self.signal_sc_index = self.training_sc_index
        self.null_sc_index = np.setdiff1d(np.array(range(0, self.n), dtype=int), self.signal_sc_index)
        self.training_signal_time = np.fft.ifft(self.training_signal_freq, n=self.n)
        self.short_training_signal_time = \
                        np.array([0.0460 + 0.0460j, -0.1324 + 0.0023j, -0.0135 - 0.0785j, 0.1428 - 0.0127j,
                                 0.0920 + 0,       0.1428 - 0.0127j, -0.0135 - 0.0785j, -0.1324 + 0.0023j,
                                 0.0460 + 0.0460j, 0.0023 - 0.1324j, -0.0785 - 0.0135j, -0.0127 + 0.1428j,
                                      0 + 0.0920j, -0.0127 + 0.1428j, -0.0785 - 0.0135j, 0.0023 - 0.1324j])

        self.preamble_sts = np.tile(self.short_training_signal_time, 10)
        self.preamble_lts = np.concatenate((self.training_signal_time[-self.cp_len * 2:],
                                               self.training_signal_time,
                                               self.training_signal_time))
        self.preamble = np.concatenate((self.preamble_sts, self.preamble_lts))

        self.preamble_sts_len = len(self.preamble_sts)
        self.preamble_lts_len = len(self.preamble_lts)

        self.shifted_index = np.array(list(range(0, int(round(self.n / 2)))) +
                                      list(range(-int(round(self.n / 2)), 0)), dtype=int)

        self.pilot_sc_index, self.data_sc_index = self.ofdm_pilot.get_pilot_and_data_index_at_symbol(0)
        self.pilot_sc_num, self.data_sc_num = self.ofdm_pilot.get_pilot_data_sc_num()
        self.n_cbps = self.data_sc_num


    @staticmethod
    def _generate_freq_ref_signal(n, pilot_pattern, pilot_num=None,
                                  training_signal_freq=None, training_sc_index=None, pilot_sc_index=None):
        assert n > 0
        # print(pilot_pattern)
        # print(pilot_num)
        # print(training_signal_freq)
        # print(training_sc_index)
        # print(pilot_sc_index)
        # assert (pilot_pattern != 'custom' and pilot_num) or \
        #        (training_signal_freq is not None and training_sc_index is not None and pilot_sc_index is not None)
        # assert not ((pilot_pattern != 'custom' and pilot_num) and
        #             (training_signal_freq is not None and training_sc_index is not None and pilot_sc_index is not None))

        if pilot_pattern != 'custom':
            index = np.random.randint(low=0, high=2, size=n)
            ref_signal_prototype = np.array([-1, 1], dtype=complex)  # BPSK for reference signal
            training_signal_freq = ref_signal_prototype[index]
            guardband_sc_num = int(np.floor(n / 5.5))  # 802.11, TODO: change it
            guardband_offset = int(np.floor(guardband_sc_num / 2))
            training_signal_freq[int(round(n / 2)) - guardband_offset:int(round(n / 2)) + guardband_offset + 1] = 0
            training_signal_freq[0] = 0  # DC
            training_sc_index_nd = np.where(training_signal_freq != 0)
            training_sc_index = training_sc_index_nd[0]

        assert training_signal_freq is not None and training_sc_index is not None and (
            pilot_num or pilot_sc_index is not None)


        if pilot_pattern == 'custom':
            ofdm_pilot = OfdmCustomPilot(training_signal_freq, training_sc_index, pilot_sc_index)
        else:
            raise Exception('invalid pilot pattern {}'.format(pilot_pattern))

        # print('training_signal_freq: {}'.format(training_signal_freq))
        # print('training_sc_index: {}'.format(training_sc_index))
        # print('ofdm_pilot: {}'.format(ofdm_pilot._pilot_sc_index))

        return training_signal_freq, training_sc_index, ofdm_pilot

    def how_many_symbols(self, data_point_num):
        return self.ofdm_pilot.how_many_symbols(data_point_num)


class OfdmPilot(object):
    def __init__(self, pilot_prototype, pilot_prototype_index, pilot_num):
        self._pilot_prototype = pilot_prototype
        self._pilot_prototype_index = pilot_prototype_index
        self._pilot_interval = int(np.floor(self._pilot_prototype_index.size / (pilot_num - 0.4)))  # fit 802.11
        self._n = self._pilot_prototype.size
        assert self._n % 2 == 0
        self._half_N = int(round(self._n / 2))

        self._signal_sc_num = self._pilot_prototype_index.size

    def get_pilot_and_data_index_at_symbol(self, symbol_index):
        """ This method should return a sorted array of pilot indices and a sorted array of data indices. """
        raise NotImplementedError

    def get_index_array_at_symbol(self, symbol_index):
        """ This method should return a tuple of two sorted array for the array indexing of
        a matrix of shape (N, ofdm_sym_num).
        """
        raise NotImplementedError

    def get_pilot_data_sc_num(self, n=None):
        """ This method should return a tuple of two integers (num of pilot sc, num of data sc) at the n-th symbol.
        If n is not given, assert the result is the same for every OFDM symbol, and return the tuple.
        """
        raise NotImplementedError

    def how_many_symbols(self, data_point_num):
        """ This method should return the number of OFDM symbols needed to convey data of size data_point_num. """
        raise NotImplementedError


class OfdmCustomPilot(OfdmPilot):
    def __init__(self, pilot_prototype, pilot_prototype_index, pilot_sc_index):
        super(OfdmCustomPilot, self).__init__(pilot_prototype, pilot_prototype_index, pilot_sc_index.size)

        self._pilot_sc_index = np.sort(pilot_sc_index)
        self._data_sc_index = np.setdiff1d(self._pilot_prototype_index, self._pilot_sc_index)

    def get_pilot_and_data_index_at_symbol(self, symbol_index):
        return self._pilot_sc_index, self._data_sc_index

    def get_index_array_at_symbol(self, symbol_index):
        assert isinstance(symbol_index, (list, tuple, np.ndarray)), 'expected list, tuple, or numpy array'
        if isinstance(symbol_index, (list, tuple)):
            col_num = len(symbol_index)
        else:
            col_num = symbol_index.size

        pilot_sc_index_array_row = np.tile(self._pilot_sc_index, (col_num, ))
        pilot_sc_index_array_col = np.repeat(symbol_index, self._pilot_sc_index.size)
        pilot_index_array = [pilot_sc_index_array_row, pilot_sc_index_array_col]

        data_sc_index_array_row = np.tile(self._data_sc_index, (col_num, ))
        data_sc_index_array_col = np.repeat(symbol_index, self._data_sc_index.size)
        data_index_array = [data_sc_index_array_row, data_sc_index_array_col]

        return pilot_index_array, data_index_array

    def get_pilot_data_sc_num(self, n=None):
        return self._pilot_sc_index.size, self._data_sc_index.size

    def how_many_symbols(self, data_point_num):
        return int(np.ceil(data_point_num / self._data_sc_index.size))



