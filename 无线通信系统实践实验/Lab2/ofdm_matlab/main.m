% Author: Lizhao You
% Date: 2025-07-01
% Func:
%   Demonstrate how to generate an OFDM packet

clear all;

% Read data
testdata = load('testdata.mat');
tx_signal = transpose(testdata.tx_signal);
preamble_lts = transpose(testdata.preamble_lts);
preamble_sts = transpose(testdata.preamble_sts);
raw_data = transpose(testdata.raw_data);

% pre-defined parameters
lts_frequency = fft(preamble_lts, 64);             % 64 FFT points
symbol_num = 20;                                   % number of data symbols
pilot_index = [8, 22, 44, 58];                     % note: pilots are arranged in this order
data_index = [2:7 9:21 23:27 39:43 45:57 59:64];   % note: data are arranged in this order
index = [1:64];
nbits = symbol_num * 48;                           % 48 data points
cp_length = 16;                                    % length of CP

% modulation
tx_samples = zeros(2500, 1);
preamble_sts_10 = repmat(preamble_sts, [10,1]);
preamble_lts_2_CP = [preamble_lts(33:end); preamble_lts; preamble_lts];
tx_samples_data = bpsk_modulation(raw_data, symbol_num, data_index, pilot_index, cp_length);
tx_samples(1:1920) = [preamble_sts_10; preamble_lts_2_CP; tx_samples_data];
