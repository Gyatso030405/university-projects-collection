function [modu] = bpsk_modulation(raw_data, sym_num, data_index, pilot_index, cp_length)
bpsk_modu = [-1+0j 1+0j];
modu = zeros(80 * sym_num, 1);
tx_data_samples_freq = zeros(64, sym_num);
for symi = 1:sym_num
    % 选择原始数据，BPSK调制
    tx_data_samples_freq(data_index, symi) = bpsk_modu(raw_data((symi-1) * 48 + 1 : symi * 48)+1);
    % 加pilot
    tx_data_samples_freq(pilot_index, symi) = [1; 1; 1; -1];
    % ifft，频域转为时域
    tx_data_samples_time = ifft(tx_data_samples_freq(:, symi), 64);
    % 加CP
    tx_data_samples_time_CP = [tx_data_samples_time(end-cp_length+1:end); tx_data_samples_time];

    modu((symi-1) * 80 + 1 : symi * 80) = tx_data_samples_time_CP;
end
end