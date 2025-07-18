# -*- coding: utf-8 -*-
# @Author  : Zhirong Tang
# @Time    : 2021/12/26 2:25 PM


import numpy as np
import binascii, random, time

SEQ_LEN = 10
RES_LEN = 16 - SEQ_LEN
CRC_LEN = 32
NSEQ = 1 << SEQ_LEN


def calc_crc32(msg_bin):
    return dec2bin(binascii.crc32(bytes(np.packbits(msg_bin))))

def check_crc32(msg_bin):
    if len(msg_bin) <= 32:
        return False
    return (msg_bin[-32:] == np.array(dec2bin(binascii.crc32(bytes(np.packbits(msg_bin[:-32])))), dtype=np.uint8)).all()

def dec2bin(num_dec, size=32):
    """ converts a decimal number to a binary numpy array
    :param num_dec:         decimal number
    :param size:        derived bit length
    :return:                binary array
    """
    bin_arr = np.array([], dtype=int)
    for _ in range(0, size):
        temp = num_dec & 0x1
        num_dec >>= 1
        bin_arr = np.append(bin_arr, temp)
    return bin_arr[::-1]

def bin2dec(bin_arr, type='left-msb'):
    """ convert a binary array to a decimal number
    :param bin_arr:      binary array
    :param type:            'left-msb' or 'right-msb'
    :return:                decimal int number
    """
    if type == 'left-msb':
        return int(''.join(str(x) for x in bin_arr), 2)
    elif type == 'right-msb':
        return int(''.join(str(x) for x in bin_arr[::-1]), 2)
    else:
        raise TypeError('Invalid type of MSB!')

def simu_pkt_loss_delay(pkt_loss_rate=0.1, mean_delay=0.3, std_delay=0.1):
    # normal distribution
    pkt_delay = random.gauss(mean_delay, std_delay)
    assert (0 < pkt_loss_rate < 1)
    pkt_delay = 0 if pkt_delay < 0 else pkt_delay
    time.sleep(pkt_delay)
    if random.random() > pkt_loss_rate:
        return True
    return False