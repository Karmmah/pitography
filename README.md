# pitography
Building a camera for photography with the Raspberry Pi HQ Camera module.

The install process is based on the process provided by Waveshare for the 1.44in LCD HAT. https://www.waveshare.com/wiki/1.44inch_LCD_HAT

0. Install RaspberryOS lite 64bit
1. clone the Git repo
2. enable SPI interface in raspi-config
```
sudo raspi-config
```
3. add executable permission to setup.sh
```
sudo chmod +x setup.sh
```
4. run setup.sh
```
./setup.sh
```
5. Increase memory allocated to the GPU by adding "gpu_mem=256" at the end of /boot/config.txt
