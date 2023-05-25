import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

import time

key1_pin = 21
key2_pin = 20
key3_pin = 16
backlight_pin = 13

# GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(key1_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(key2_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(key3_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(backlight_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT, initial=1)

# display with hardware SPI
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# draw initial image
width, height = 128, 128
image = Image.new("RGB", (width,height))
draw = ImageDraw.Draw(image)
#draw.rectangle((0,0,width,height), outline=0, fill=1)
#disp.LCD_ShowImage(image,0,0)

def main(image):
	grid = 3
	square_size = width/grid

	#color coding: 0x blue green red
#	colors = [0xff0000, 0x990000, 0x440000,	0x00ff00, 0x009900, 0x004400, 0x0000ff, 0x000099, 0x000044]
	colors = [0x0000ff, 0x000099, 0x000044,	0x00ff00, 0x009900, 0x004400, 0xff0000, 0x990000, 0x440000]

	for row in range(grid):
		for column in range(grid):
			x1, y1 = square_size*column, square_size*row
			x2, y2 = square_size*column + square_size, square_size*row + square_size

#			draw.rectangle( (x1,y1,x2,y2), outline=0, fill=colors[row*grid+column] )
#			draw.rectangle( (x1,y1,x2,y2), outline=colors[row*grid+column], width=5 )
#			draw.rectangle( (x1,y1,x2,y2), outline=colors[row*grid+column], width=5, fill=0xffffff )
			draw.rectangle( (x1,y1,x2,y2), fill=colors[row*grid+column] )
#			draw.rectangle( (x1,y1,x2,y2), fill=colors[len(colors)-1-(row*grid+column)], outline=colors[row*grid+column], width=3 )

	draw.text( (width/2,10), "Test", fill=0xffffff, align="center", anchor="center" )

	center = (10,70)
	draw.rectangle( (center[0]-11,center[1]-11,center[0]+11,center[1]+11), fill=0x00d0ff)
	center = (10,50)
	draw.rectangle( (center[0]-9,center[1]-9,center[0]+9,center[1]+9), fill=0xff3050)
	center = (10,30)
	draw.rectangle( (center[0]-7,center[1]-7,center[0]+7,center[1]+7), fill=0x000000)
	center = (10,10)
	draw.rectangle( (center[0]-5,center[1]-5,center[0]+5,center[1]+5), fill=0xffffff)

	image = image.rotate(180)

#	while True:
#		if GPIO.input(backlight_pin) == 0:
#			GPIO.output(24, 0)
#		else:
#			GPIO.output(24, 1)

#		disp.LCD_ShowImage(image, 0, 0)

	disp.LCD_ShowImage(image, 0, 0)
	time.sleep(2)

try:
	if __name__ == "__main__":
		main(image)

#except:
#	print("ERROR")

finally:
	print("\nProgram stopped")
	GPIO.cleanup()
	print("GPIO.cleanup()")
