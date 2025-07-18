# Automatical environment setup for XMU-SDR in Ubuntu 18.04
# Date:	2021-12-09
#!/usr/bin/bash

# Install Miniconda3
sudo mkdir -p /opt
sudo chmod -R 777 /opt
set -e
wget "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh" -O /opt/miniconda3.sh --no-check-certificate
bash /opt/miniconda3.sh -b -p /opt/miniconda3
/opt/miniconda3/bin/conda init $(echo $SHELL | awk -F '/' '{print $NF}')
echo 'Successfully installed miniconda3...'
echo -n 'Conda version: '
/opt/miniconda3/bin/conda --version
sudo chmod -R 777 /opt/miniconda3
source ~/.bashrc

# Install dependencies
sudo apt-get install git libxml2 libxml2-dev bison flex libcdk5-dev cmake \
libusb-1.0-0 libusb-1.0-0-dev  libavahi-common-dev libavahi-client-dev libaio-dev -y

# Install libiio
cd /opt/
# git clone --branch v0.23 https://github.com/analogdevicesinc/libiio.git
git clone --branch v0.23 https://gitee.com/ttangzr/libiio.git libiio
cd libiio
cmake ./
make all -j4
sudo make install
sudo ldconfig
cd bindings/python/
sudo python3 setup.py.cmakein install

# Install libadi9361
cd /opt/
# git clone --branch v0.2 https://github.com/analogdevicesinc/libad9361-iio.git
git clone --branch v0.2 https://gitee.com/ttangzr/libad9361-iio.git libad9361-iio
cd libad9361-iio
cmake ./
make -j4
sudo make install

# Install pyadi-iio
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyadi-iio==0.0.11

echo -e "\n=================>Installation Done!=================>\n"
exec bash
