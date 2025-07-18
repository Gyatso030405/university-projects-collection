# -*- coding: utf-8 -*-

# compatibility of Python 2/3
from __future__ import division
from __future__ import print_function
from builtins import object

import numpy as np

# from sympy.combinatorics.graycode import GrayCode
from gray_code import GrayCode


class GrayQamMod(object):
    def __init__(self, m):
        """
        gray-coded QAM modulation
        Big endian
        :param m: modulation size, restricted to the form 2^(2*q)
        """
        super(GrayQamMod, self).__init__()
        assert np.mod(np.log2(m), 1) < 1e-10  # integer bits
        assert np.mod(np.sqrt(m), 1) == 0 or m == 2 # the constellation is restricted to MxM presently
        self.m = m
        self.bit_num = int(round(np.log2(m)))
        self.p = int(round(np.sqrt(m)))  # m = p^2
        if m == 2:
            self.qam_max_axis = 1
        else:
            self.qam_max_axis = np.sqrt(m) - 1
        # code = GrayCode(self.bit_num)
        # gray_map_str = list(code.generate_gray())
        gray_map_str = GrayCode(self.bit_num)
        idx_to_gray = np.array([int(ci, 2) for ci in gray_map_str], dtype=int)
        gray_to_idx = np.argsort(idx_to_gray)

        idx_to_constel = np.zeros((m, ), dtype=complex)
        xi = 0
        xq = 0
        inc_sign = 1
        for idx in range(0, m):
            idx_to_constel[idx] = -self.qam_max_axis - 1j*self.qam_max_axis + xi*2 + 1j*xq*2
            if (inc_sign == 1 and xq == self.p-1) or (inc_sign == -1 and xq == 0):
                xi += 1
                inc_sign *= -1
            else:
                xq += inc_sign

        self.gray_to_constel = idx_to_constel[gray_to_idx]

        bit_powers = np.array([2 ** (self.bit_num - 1 - bi) for bi in range(0, self.bit_num)], dtype=int)
        self.bit_powers = np.reshape(bit_powers, (bit_powers.size, 1))  # col vector

    def _dec2bin(self, s):
        bin_mat = np.zeros((self.bit_num, s.size), dtype=int)
        for si in range(0, s.size):
            tt = np.array(list(np.binary_repr(s[si], width=self.bit_num)), dtype=int)
            # list() converts '1101' to '1','1','0','1'
            bin_mat[:, si] = tt

        return np.reshape(bin_mat, (bin_mat.size, ), order='F')

    def modulate(self, b):
        """
        modulate bits to complex symbols
        :param b: 1-D array-like bits
        :return: 1-D array modulated complex symbols
        """
        if np.mod(b.size, self.bit_num) != 0:
            pad_bit_num = self.bit_num - np.mod(b.size, self.bit_num)
            b = np.concatenate((b, np.zeros(pad_bit_num, dtype=b.dtype)))
        if self.bit_num == 1:
            symbols = b * 2 - np.ones(b.size)
            return symbols
        else:
            sym_num = int(b.size / self.bit_num)
            b_mat = np.reshape(b, (self.bit_num, sym_num), order='F')  # each column is the bits for one symbol, MSB first
            symbols = np.sum(np.multiply(self.bit_powers, b_mat), axis=0)
            symbols = np.reshape(symbols, (symbols.size,))

            return self.gray_to_constel[symbols]


