
> - Author: Lizhao You
> - Date: 2025-07-01

## 发送基带信号

.npy: 数据文件

.m: Matlab代码

- tx_signal.npy: 一个完整数据包的基带信号
- preamble_sts.npy: 16 samples STS
- preamble_lts.npy: 64 samples LTS
- npy_to_mat.py: 将npy文件转成matlab能读取的mat格式

## Lab1采集的基带信号

- recorded_signal_strong.npy: 采集的基带信号
- raw_data.npy: 对应的比特数据

## Lab2新采集的基带信号

- recorded_signal_10sym.npy: 10 data symbols
- recorded_signal_100sym.npy: 100 data symbols

## 参考代码

- ofdm_matlab/: OFDM发送机的Matlab参考代码
- ofdm_python/: 
  - OFDM发送机的python参考代码: transmitter.py
  - 用于采集基带信号的python接收机参考代码: receiver.py
