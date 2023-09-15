#!/bin/sh

echo Install BCM2835 libraries
cd ~
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
#./configure && make && make check && make install

echo Install WiringPi
cd ~
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v

echo Create folder for taken images
cd ~
mkdir DCIM

echo Add and enable camera to systemctl
cd ~/pitography
sudo cp camera.service /etc/systemd/system/
sudo systemctl enable camera.service

echo Add and enable file server
# file server to access the images taken over the local network via the ip address
cd ~/pitography
sudo cp file_server.service /etc/systemd/system/file_server.service
sudo systemctl enable file_server
#cp file_server.service /etc/systemd/system/file_server.service
#systemctl enable file_server
