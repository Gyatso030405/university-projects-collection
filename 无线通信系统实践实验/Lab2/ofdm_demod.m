% === 解调函数定义 ===
function [bits, H] = ofdm_demod(rx_signal, start_idx, fft_len, cp_len, st_len, lt_len, data_indices)
    % 提取LTS，信道估计
    lts1 = rx_signal(start_idx + st_len + 33 : start_idx + st_len + 96);
    lts2 = rx_signal(start_idx + st_len + 97 : start_idx + st_len + 160);
    H = (fftshift(fft(lts1, fft_len)) + fftshift(fft(lts2, fft_len))) / 2;

    % 提取数据部分
    payload_start = start_idx + st_len + lt_len + 1;
    payload = rx_signal(payload_start:end);

    symbol_len = cp_len + fft_len;
    num_symbols = floor(length(payload) / symbol_len);
    bits = [];

    for i = 0:num_symbols-1
        base = i * symbol_len;
        symbol = payload(base + cp_len + 1 : base + cp_len + fft_len);
        symbol_freq = fftshift(fft(symbol));
        equalized = symbol_freq ./ H;
        subcarriers = equalized(data_indices);
        b = real(subcarriers) > 0;
        bits = [bits; b(:)];
    end
end
