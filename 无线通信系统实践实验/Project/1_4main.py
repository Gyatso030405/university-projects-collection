import math
import time
import numpy as np
from test_read_save_img import read_image, save_image
from ofdm.ofdm_tx import OfdmTx
from ofdm.ofdm_rx import OfdmRx
from llc.llc_nodeA import NodeALLC
from llc.llc_nodeB import NodeBLLC

def main():
    # 参数配置
    pkt_size = 20 * 48  # 你NodeALLC/NodeBLLC里packet_bit_size大小
    img_path = "images/xmu1.jpg"
    recv_save_path = "recv_img.jpg"

    phy_type = "socket"
    tx_args = ("127.0.0.1", 52001)
    rx_args = ("127.0.0.1", 52002)

    # 读取图片，得到bit流
    bits = list(read_image(img_path))
    print(f"[Main] Loaded image bits: {len(bits)}")

    # 创建OFDM实例
    ofdm_tx_A = OfdmTx(phy_type, tx_args)
    ofdm_rx_A = OfdmRx(phy_type, rx_args)
    ofdm_tx_B = OfdmTx(phy_type, rx_args)
    ofdm_rx_B = OfdmRx(phy_type, tx_args)

    # 创建节点实例，传入socket地址和packet大小
     # 创建节点实例
    nodeA = NodeALLC(ofdm_tx_A, ofdm_rx_A, packet_bit_size=pkt_size)
    nodeB = NodeBLLC(ofdm_tx_B, ofdm_rx_B, packet_bit_size=pkt_size)
    #nodeA = NodeALLC(phy_type, tx_args=tx_args, rx_args=rx_args, packet_bit_size=pkt_size)
    #nodeB = NodeBLLC(phy_type, tx_args=rx_args, rx_args=tx_args, packet_bit_size=pkt_size)

    # 启动接收线程NodeB（先启动接收端）
    nodeB.start()
    time.sleep(1)  # 等待接收端准备好

    # 发送图片bit流（阻塞式，发送完退出）
    nodeA.send(bits, arq_mode="stop-and-wait-ARQ")

    # 发送完成，停止接收端线程
    nodeB.done()
    nodeB.join()

    # 获取接收到的bits，保存为图片
    rx_bits = nodeB.get_received_bits()
    save_image(rx_bits, recv_save_path)
    print(f"[Main] Received image saved to: {recv_save_path}")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
