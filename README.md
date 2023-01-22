# pi_camera
Building a camera for photography with the Raspberry Pi HQ Camera module.

The install process is based on the process provided by Waveshare for the 1.44in LCD HAT. https://www.waveshare.com/wiki/1.44inch_LCD_HAT

0. Install RaspberryOS lite 32bit
1. Enable SPI-Interface and Camera Interface on Raspberry Pi, then reboot
```
sudo raspi-config
```
2. Install BCM2835 libraries
```
cd ~
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```
3. Install WiringPi
```
cd ~
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
5. Add Camera service to systemctl
```
cd ~/pi_camera
sudo cp camera.service /etc/systemd/system/camera.service
sudo systemctl enable camera
```
6. Create folder to save images to
```
mkdir ~/DCIM
```
7. Increase available GPU memory to enable highest resolution capture
```
# change value of gpu_mem to 256
sudo nano /boot/config.txt
```
8. Optional: Download code samples
```
cd ~
sudo apt install p7zip-full -y
wget https://www.waveshare.com/w/upload/f/fa/1.44inch-LCD-HAT-Code.7z
7z x 1.44inch-LCD-HAT-Code.7z
sudo chmod 777 -R 1.44inch-LCD-HAT-Code
cd 1.44inch-LCD-HAT-Code/RaspberryPi/
```
