import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

key1_pin = 21
key2_pin = 20
key3_pin = 16

# GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setup(key1_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(key2_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(key3_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
disp.LCD_ShowImage(image,0,0)

def main():
	while True:
#		if GPIO.input(key1_pin) == 0:
#			draw.rectangle((22,50,50,height-50), outline=0, fill=0xf0f0)
#			print("key1")
#		else:
#			draw.rectangle((22,50,50,height-50), outline=0, fill=0x222f)
#
#		if GPIO.input(key2_pin) == 0:
#			draw.rectangle((50,50,width-50,height-50), outline=0, fill=0xf00f)
#			print("key2")
#		else:
#			draw.rectangle((50,50,width-50,height-50), outline=0, fill=0x2226)
#
#		if GPIO.input(key3_pin) == 0:
#			draw.rectangle((width-50,50,width-22,height-50), outline=0, fill=0x00ff)
#			print("key3")
#		else:
#			draw.rectangle((width-50,50,width-22,height-50), outline=0, fill=0x2220)

		grid = 3
		square_size = width/grid

		colors = [0xff0000, 0x990000, 0x440000,
				0x00ff00, 0x009900, 0x004400,
				0x0000ff, 0x000099, 0x000044]
		for row in range(grid):
			for column in range(grid):
				x1, y1 = square_size*column, square_size*row
				x2, y2 = square_size*column + square_size, square_size*row + square_size

#				hex_color = hex( 16384*row + 4096*(column+1) -1 )
#				print(hex_color)

				draw.rectangle( (x1,y1,x2,y2), outline=0, fill=colors[row*grid+column] )
#				draw.rectangle( (x1,y1,x2,y2), outline=0, fill=hex_color )
#				draw.rectangle( (x1,y1,x2,y2), outline=0, fill="#abcdef" )

		disp.LCD_ShowImage(image, 0, 0)

try:
	if __name__ == "__main__":
		main()

#except:
#	print("ERROR")

finally:
	print("Program stopped: GPIO.cleanup()")
	GPIO.cleanup()
