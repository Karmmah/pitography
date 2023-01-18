# pi_camera
Building a camera for photography with the Raspberry Pi HQ Camera module.

0. Install RaspberryOS lite 32bit
1. Enable SPI-Interface and Camera Interface on Raspberry Pi, then reboot
```
sudo raspi-config
```
2. Install BCM2835 libraries
```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```
3. Install WiringPi
```
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# Run gpio -v and version 2.60 or higher will appear. If it does not appear, it means that there is an installation error
```
4. Install python libraries
```
sudo apt update
sudo apt install python3-pip
sudo apt install python3-pil
sudo apt install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo pip3 install picamera
```
5. Copy .service file to: /etc/systemd/system to enable autostart at Pi startup
