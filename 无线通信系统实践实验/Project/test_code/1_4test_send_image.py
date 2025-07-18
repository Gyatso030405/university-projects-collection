from llc.llc_nodeA import NodeALLC
from llc.llc_utils import bin2dec, dec2bin
from test_read_save_img import read_image
import time

if __name__ == "__main__":
    nodeA = NodeALLC("socket", tx_args=("127.0.0.1", 52002), rx_args=("127.0.0.1", 52003))
    bits = read_image("images/xmu2.jpg")  # 读取图片为bit流

    pkt_len = nodeA.max_payload_len
    num_pkt = (len(bits) + pkt_len - 1) // pkt_len

    for i in range(num_pkt):
        payload = bits[i * pkt_len: (i + 1) * pkt_len]
        nodeA.send(payload)  # 调用封装好的ARQ发送
        time.sleep(0.01)
