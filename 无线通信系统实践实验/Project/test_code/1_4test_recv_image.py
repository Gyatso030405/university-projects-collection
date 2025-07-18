from llc.llc_nodeB import NodeBLLC
from test_read_save_img import save_image

if __name__ == "__main__":
    nodeB = NodeBLLC("socket", tx_args=("127.0.0.1", 52003), rx_args=("127.0.0.1", 52002))
    bitstream = []

    while True:
        data = nodeB.recv()
        if data is not None:
            bitstream.extend(data)
            print(f"[Recv] Received {len(data)} bits, total: {len(bitstream)}")
            # 如果知道bit流长度可以设置 break 条件
        if len(bitstream) > 400000:  # 示例终止条件（图像大小估计）
            break

    save_image(bitstream, "images/recv.jpg")
