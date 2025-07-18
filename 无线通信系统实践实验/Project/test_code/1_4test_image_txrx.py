import math
import numpy as np
from test_read_save_img import read_image, save_image
from llc.llc_img_txrx import NodeALLC, NodeBLLC


def main():
    # 基本配置
    pkt_size = 100 * 48 - 16 - 32
    img_path = "images/xmu1.jpg"
    rx_save_path = "images/recv.jpg"
    phy_type = "socket"

    tx_args = ("127.0.0.1", 52001)
    rx_args = ("127.0.0.1", 52002)

    # 加载图像
    bits = list(read_image(img_path))
    print("[Main] Loaded image: {} bits".format(len(bits)))

    # 初始化 LLC 节点
    nodeA = NodeALLC(phy_type, tx_args=tx_args, rx_args=rx_args, packet_bit_size=pkt_size)
    nodeB = NodeBLLC(phy_type, tx_args=rx_args, rx_args=tx_args, packet_bit_size=pkt_size)

    # 启动节点
    nodeB.start()
    nodeA.start()

    # 发送图像数据（带停止等待ARQ）
    nodeA.send(bits, arq_mode="stop-and-wait-ARQ")

    # 等待结束
    nodeA.join()
    nodeB.join()

    # 保存接收到的图像
    rx_bits = nodeB.get_received_bits()
    save_image(rx_bits, rx_save_path)
    print("[Main] Image saved to:", rx_save_path)


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
