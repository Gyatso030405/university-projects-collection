% 实验1.1 - 解调tx_signal（无失真）
% 文件: ofdm_rx_lab1_1.m

clear; clc;

% === 参数设定 ===
FFT_LEN = 64;
CP_LEN = 16;
ST_LEN = 160;
LT_LEN = 160;

% 子载波索引
data_indices = [ ...
     1:6, 8:20, 22:26, ...
    -26:-22, -20:-8, -6:-1 ...
] + FFT_LEN/2 + 1;  % MATLAB从1开始索引，+33

% === 载入数据 ===
load('testdata.mat');  % 包含 tx_signal, preamble_lts, preamble_sts, raw_data

% === 提取数据区域 ===
payload_start = ST_LEN + LT_LEN + 1;
rx_signal = tx_signal(:);
payload = rx_signal(payload_start:end);

% === 分割为多个OFDM符号 ===
symbol_len = CP_LEN + FFT_LEN;
num_symbols = floor(length(payload) / symbol_len);
demod_bits = [];

for i = 0:num_symbols-1
    start_idx = i * symbol_len + 1;
    symbol_with_cp = payload(start_idx : start_idx + symbol_len - 1);
    symbol = symbol_with_cp(CP_LEN + 1:end);
    
    % FFT
    freq_data = fftshift(fft(symbol, FFT_LEN));
    
    % 提取数据子载波
    data_subcarriers = freq_data(data_indices);
    
    % BPSK判决
    bits = real(data_subcarriers) > 0;
    demod_bits = [demod_bits; bits];
end

% === 对比原始数据 ===
rx_bits = demod_bits(1:length(raw_data));
num_correct = sum(rx_bits == raw_data(:));
accuracy = num_correct / length(raw_data) * 100;

fprintf("解调完成！总比特数: %d, 正确数: %d, 正确率: %.2f%%\n", ...
    length(raw_data), num_correct, accuracy);
