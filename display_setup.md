Link to website: https://www.waveshare.com/wiki/1.44inch_LCD_HAT

Contents (16.01.2023):

# 1.44inch LCD HAT

1.44inch-LCD-HAT-1.jpg
1.44inch LCD HAT, SPI interfaces

## Overview
### Introduction

1.44inch LCD HAT, SPI interfaces
More

### Specification

    Operating voltage: 3.3V
    Interface: SPI
    LCD type: TFT
    Controller: ST7735S
    Resolution: 128*128 (Pixel)
    Display size: 25.5*26.5（mm）
    Pixel size: 0.129(W)*0.219 (H)(MM)
    Dimension: 65 x 30.2 (mm)

### Pinout
PIN 	Raspberry Pi Interface (BCM) 	Description
---
KEY1 	P21 	KEY1GPIO
KEY2 	P20 	KEY2GPIO
KEY3 	P16 	KEY3GPIO
Joystick UP 	P6 	Upward direction of the Joystick
Joystick Down 	P19 	Downward direction of the Joystick
Joystick Left 	P5 	Left direction of the Joystick
Joystick Right 	P26 	Right direction of the Joystick
Joystick Press 	P13 	Press the Joystick
SCLK 	P11/SCLK 	SPI clock line
MOSI 	P10/MOS 	SPI data line
CS 	P8/CE0 	Chip selection
DC 	P25 	Data/Command control
RST 	P27 	Reset
BL 	P24 	Backlight
LCD and the controller

The ST7735S is a 132*162 pixel LCD controller, but the pixel of the 1.44inch LCD HAT is 128*128. So we have made some processing on the display: the horizontal direction starts from the second pixel to guarantee the location of RAM in the LCD is consistent with the actual location at the same time.
This LCD accepts 8-bits/9-bits/16-bits/18-bits parallel interface, that are RGB444, RGB565, RGB666. The color format used in demo codes is RGB565.
This LCD uses 4-wire SPI interface for reducing GPIO, and the communication speed will be faster.

### Working Protocol

0.96inch lcd module spi.png

Note: Different from the traditional SPI protocol, the data line from the slave to the master is hidden since the device only has a display requirement.
RESX Is the reset pin, it should be low when powering the module and be higher at other times.
CSX is slave chip select, when CS is low, the chip is enabled.
D/CX is data/command control pin, when DC = 0, write command, when DC = 1, write data
SDA is the data pin for transmitting RGB data, it works as the MOSI pin of the SPI interface;
SCL works the SCLK pins of the SPI interface.
SPI communication has data transfer timing, which is combined by CPHA and CPOL.
CPOL determines the level of the serial synchronous clock at an idle state. When CPOL = 0, the level is Low. However, CPOL has little effect on the transmission.
CPHA determines whether data is collected at the first clock edge or at the second clock edge of the serial synchronous clock; when CPHL = 0, data is collected at the first clock edge.
There are 4 SPI communication modes. SPI0 is commonly used, in which CPHL = 0, CPOL = 0.

## Working with Raspberry
### Enable SPI interface
PS: If you are using the system of the Bullseye branch, you need to change "apt-get" to "apt", the system of the Bullseye branch only supports Python3.
RPI open spi.png

Open terminal, use command to enter the configuration page

`sudo raspi-config
Choose Interfacing Options -> SPI -> Yes  to enable SPI interface`

Reboot Raspberry Pi：

`sudo reboot`

Please make sure the SPI is not occupied by other devices, you can check in the middle of /boot/config.txt

### Install Libraries

    Install BCM2835 libraries

#Open the Raspberry Pi terminal and run the following command
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
# For more information, please refer to the official website: http://www.airspayce.com/mikem/bcm2835/

    Install wiringPi libraries

#Open the Raspberry Pi terminal and run the following command
sudo apt-get install wiringpi
#For Raspberry Pi systems after May 2019 (earlier than before, you may not need to execute), you may need to upgrade:
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
# Run gpio -v and version 2.52 will appear. If it does not appear, the installation is wrong

#Bullseye branch system use the following command:
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# Run gpio -v and version 2.60 will appear. If it does not appear, it means that there is an installation error

    Install Python libraries

#python2
sudo apt-get update
sudo apt-get install python-pip
sudo apt-get install python-pil
sudo apt-get install python-numpy
sudo pip install RPi.GPIO
sudo pip install spidev
#python3
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev

### Download Examples

Open Raspberry Pi terminal and run the following command

sudo apt-get install p7zip-full -y
wget https://www.waveshare.com/w/upload/f/fa/1.44inch-LCD-HAT-Code.7z
7z x 1.44inch-LCD-HAT-Code.7z
sudo chmod 777 -R 1.44inch-LCD-HAT-Code
cd 1.44inch-LCD-HAT-Code/RaspberryPi/

### Test Program
#### C codes

cd c
sudo make clean
make 
sudo ./main

For Raspberry Pi 4B and the system later than raspbian_lite-2019-06-20, you need to set as follows, and the key can be input normally

sudo nano /boot/config.txt
#Add the following:
gpio=6,19,5,26,13,21,20,16=pu

#### python

cd python
sudo python main.py
sudo python key_demo.py

## FBCP Driver

The Framebuffer uses a memory area to store the display content, and changes the data in the memory to change the display content.

There is an open-source project on github: fbcp-ili9341. Compared with other fbcp projects, this project uses partial refresh and DMA to achieve a refresh rate of up to 60fps.

### Compile and Run

cd ~
sudo apt-get install cmake -y
sudo apt-get install p7zip-full -y
wget https://www.waveshare.com/w/upload/f/f9/Waveshare_fbcp.7z
7z x Waveshare_fbcp.7z -o./waveshare_fbcp
cd waveshare_fbcp
mkdir build
cd build

If you are using 1.44inch_LCD_HAT:

cmake -DSPI_BUS_CLOCK_DIVISOR=20 -DWAVESHARE_1INCH44_LCD_HAT=ON -DBACKLIGHT_CONTROL=ON -DSTATISTICS=0 ..

If you are using 1.3inch_LCD_HAT:

cmake -DSPI_BUS_CLOCK_DIVISOR=20 -DWAVESHARE_1INCH3_LCD_HAT=ON -DBACKLIGHT_CONTROL=ON -DSTATISTICS=0 ..

Then

make -j
sudo ./fbcp

### Auto-start when Power on
1in3 lcd fb5.png

sudo cp ~/waveshare_fbcp/build/fbcp /usr/local/bin/fbcp
sudo nano /etc/rc.local

And then add fbcp& before exit 0, as the picture below.

### Set the Display Resolution

Set the user interface display size in the /boot/config.txt file.

sudo nano /boot/config.txt

Then add the following lines at the end of the config.txt.

hdmi_force_hotplug=1
hdmi_cvt=300 300 60 1 0 0 0
hdmi_group=2
hdmi_mode=87
display_rotate=0

【Note】If you are using Raspberry Pi 4B, you need to comment out the following lines on the [pi4] part. The modification is as below:

[pi4]
# Enable DRM VC4 V3D driver on top of the dispmanx display stack
#dtoverlay=vc4-fkms-v3d
#max_framebuffers=2

And then reboot the system

sudo reboot

The final display effect is scaled and displayed on the 1.3inch LCD in proportion. The setting of the resolution here should be slightly larger than the LCD resolution, the too high resolution will cause the font display to be blurred.

After rebooting the system, the Raspberry Pi OS user interface will be displayed.

1200px-1.3inch lcd hat fbtftdesktop.png

### Analog Mouse

There are a joystick and three buttons on the panel of the module, which we can use to control the mouse of the Raspberry Pi.

    Install the library, then download and run the demo.

#python2
sudo apt-get install python-xlib
sudo pip install PyMouse
wget https://www.waveshare.com/w/upload/d/d3/Mouse.7z
7z x Mouse.7z
sudo python mouse.py
#python3
sudo apt-get install python3-xlib
sudo pip3 install PyMouse
sudo pip3 install unix
sudo pip3 install PyUserInput
wget http://www.waveshare.net/w/upload/d/d3/Mouse.7z
7z x Mouse.7z
sudo python3 mouse.py

    【Note】The mouse.py needs to run under the graphical interface, which will not run under the SSH login. You can skip this step directly, the Pi will run the demo automatically by booting up.
    If you are using the Raspberry PI 4B and the version of your image is after raspbian_lite-2019-06-20, you need to set it as below:

sudo nano /boot/config.txt

And then add the following line at the end of the config.txt.

gpio=6,19,5,26,13,21,20,16=pu

Use the joystick to move up, down, left, and right, you can see that the mouse is moving.

    Set the auto-start when power on

Be careful not to add it to /etc/rc.local, because rc.local will be executed before the system enters the desktop, and if the PyMouse module runs on the command line interface, it will report an error that there is no mouse event, so we need to execute the following:

cd .config/
mkdir autostart
cd autostart/
sudo nano local.desktop

And then add the following lines at the end of the local.desktop

#python2
[Desktop Entry]
Type=Application
Exec=python /home/pi/mouse.py
#python3
[Desktop Entry]
Type=Application
Exec=python3 /home/pi/mouse.py

Reboot the system, you can use the buttons to control the mouse.

sudo reboot
