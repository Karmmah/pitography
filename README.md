# pitography
Building a camera for photography with the Raspberry Pi HQ Camera module.

![camera front view](https://scontent-dus1-1.cdninstagram.com/v/t51.29350-15/453399245_1478209389503486_1521032123887766358_n.jpg?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xNDQweDE0NDAuc2RyLmYyOTM1MCJ9&_nc_ht=scontent-dus1-1.cdninstagram.com&_nc_cat=102&_nc_ohc=DtYeX1RXf2gQ7kNvgFecldt&edm=AEhyXUkBAAAA&ccb=7-5&ig_cache_key=MzQyMjI2Mjg4MjYyOTk0NDUyMw%3D%3D.2-ccb7-5&oh=00_AYDkW1rzHSnqanL32AY55nY4CdTGhKFF8Q0IHltnoHnjQg&oe=66AD2DA6&_nc_sid=8f1549)
![camera back view](https://scontent-dus1-1.cdninstagram.com/v/t51.29350-15/453378072_1182047296445009_4853404648570295119_n.jpg?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xNDQweDE0NDAuc2RyLmYyOTM1MCJ9&_nc_ht=scontent-dus1-1.cdninstagram.com&_nc_cat=105&_nc_ohc=qJcY_omyLMgQ7kNvgEgSNft&edm=AEhyXUkBAAAA&ccb=7-5&ig_cache_key=MzQyMjI2Mjg4MjYyOTkyNTM4MQ%3D%3D.2-ccb7-5&oh=00_AYBIEc14RjPIRSr5-c72Z5b7j-2B2hQefGjdK-_PQshobA&oe=66AD1C0F&_nc_sid=8f1549)

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
