# pitography
Building a camera for photography with the Raspberry Pi HQ Camera module.

The install process is based on the process provided by Waveshare for the 1.44in LCD HAT. https://www.waveshare.com/wiki/1.44inch_LCD_HAT

0. Install RaspberryOS lite 64bit
1. Clone this git repository
2. Enable SPI interface in raspi-config
```
sudo raspi-config
```
3. Run setup.sh
```
sh setup.sh
```
4. Increase memory allocated to the GPU by adding "gpu_mem=256" at the end of /boot/config.txt
```
echo "gpu_mem=256" >> /boot/config.txt
```

## Create timelapse with ffmpeg

- install ffmpeg
- example command:
	ffmpeg -framerate 30 -i <path>/<timelapse_name>_%04d.jpg -vf "scale=1920:-1" -q 4 output.mp4
	- framerate: output framerate
	- i: input file name pattern (here with 4-digit number padded with zeros)
	- vf: "video filter" to scale video to desired resolution (-1 to keep aspect ratio with desired 1920 resolution)
	- q: quality in range 1 (best, large file) - 31 (worst, small file)
