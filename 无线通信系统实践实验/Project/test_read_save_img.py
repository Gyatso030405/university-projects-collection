# -*- coding: utf-8 -*-
# @Author  : Zhirong Tang
# @Time    : 2022/4/26 08:46


import math
import numpy as np
from PIL import Image


def read_image(img_path):
    print("Load image from:", img_path)
    # open the img
    img = Image.open(img_path)
    mode = img.mode
    if mode == 'RGB':
        greyLevel = 3
    elif mode == 'L':
        greyLevel = 1
    else:
        greyLevel = 1
    img_data = np.array(list(img.getdata()), dtype=np.uint8)
    img_data.shape = len(img_data) * greyLevel, 1

    width, height = img.size
    width1 = width // 128
    width2 = width % 128
    height1 = height // 128
    height2 = height % 128

    pkt = [width1, width2, height1, height2, greyLevel]  # 1 indicates grey-level
    print("Image info: width:{}, height:{}, greyLevel:{}".format(width, height, greyLevel))
    for i in range(len(img_data)):
        pkt.append(img_data[i][0])
    return np.unpackbits(np.array(pkt, dtype=np.uint8))

def extract_image_info(pkt):
    print("Extracting image info.")
    _pkt = np.packbits(pkt)
    width1, width2, height1, height2, greyLevel = _pkt[0: 5]
    width = width1 * 128 + width2
    height = height1 * 128 + height2
    print("Image info: width:{}, height:{}, greyLevel:{}".format(width, height, greyLevel))
    return width, height, greyLevel

def save_image(pkt, save_path):
    print("Save image to:", save_path)
    width, height, greyLevel = extract_image_info(pkt)
    _pkt = np.packbits(pkt)
    img_data = np.array(_pkt[5: 5 + width * height * greyLevel], dtype=np.uint8)
    if greyLevel == 3:
        img_data.shape = height, width, greyLevel
        img = Image.fromarray(img_data).convert('RGB')
    elif greyLevel == 1:
        img_data.shape = height, width
        img = Image.fromarray(img_data).convert('L')
    else:
        raise ValueError("Grey level not supported!")
    img.save(save_path)

if __name__ == '__main__':
    # PHY example, assumed that we can support OFDM PHY with 100 symbols
    pkt_size = 100 * 48 - 16 - 32

    # tx
    tx_pkt = list(read_image(r'images/xmu2.jpg'))
    width, height, greyLevel = extract_image_info(tx_pkt)
    num_frame = math.ceil(len(tx_pkt) / pkt_size)

    # rx
    rx_pkt = [0] * num_frame * pkt_size
    for n in range(num_frame):
        rx_pkt[n*pkt_size: (n+1)*pkt_size] = tx_pkt[n*pkt_size: (n+1)*pkt_size]
    save_image(rx_pkt, r'images/recv.jpg')