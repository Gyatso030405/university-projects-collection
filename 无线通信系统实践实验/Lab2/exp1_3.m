% 文件名：ofdm_rx_lab1_3_all.m
% 实验1.3：解调 recorded_signal_10sym 和 recorded_signal_100sym

clear; clc;

% === 参数设定 ===
FFT_LEN = 64;
CP_LEN = 16;
ST_LEN = 160;
LT_LEN = 160;

% 子载波索引（+33 是因为 MATLAB 从1开始）
data_indices = [ ...
     1:6, 8:20, 22:26, ...
    -26:-22, -20:-8, -6:-1 ...
] + FFT_LEN/2 + 1;


% ========== 解调第一个文件 ==========
disp("=== 解调 recorded_signal_10sym.mat ===");
load('recorded_signal_10sym.mat');  % 变量名 rx10
start_10 = 2649;  

[bits10, H10] = ofdm_demod(rx10, start_10, FFT_LEN, CP_LEN, ST_LEN, LT_LEN, data_indices);
disp('recorded_signal_10sym 的前20比特:');
disp(bits10(1:20)');

save('lab1_3_rx_bits_10sym.mat', 'bits10');

% ========== 解调第二个文件 ==========
disp("=== 解调 recorded_signal_100sym.mat ===");
load('recorded_signal_100sym.mat');  % 变量名 rx100
start_100 = 2649;  % 通常和10sym是一样的起点（如果实验中没变化）

[bits100, H100] = ofdm_demod(rx100, start_100, FFT_LEN, CP_LEN, ST_LEN, LT_LEN, data_indices);
disp('recorded_signal_100sym 的前20比特:');
disp(bits100(1:20)');

save('lab1_3_rx_bits_100sym.mat', 'bits100');
