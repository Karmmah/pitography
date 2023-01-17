import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

import time
import picamera as pc

# button mapping
shutter_pin = 13

# display with hardware SPI
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# draw initial image
ui_width, ui_height = 128, 128
ui = Image.new("RGB", (ui_width,ui_height))
draw = ImageDraw.Draw(ui)

# GPIO init
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()
GPIO.setup(shutter_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def main(ui, cam):
	draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
	disp.LCD_ShowImage(ui, 0, 0)

	cam.crop = (0,0,1,1)

	ui.rotate(180)

	print("Starting the program loop")
	while True:
		# capture image
		if GPIO.input(shutter_pin) == 0:
#			cam.resolution = (4056,3040)
			cam.resolution = (2028,1520)
			cam.rotation = 0
			cam.capture( "/home/pi/DCIM/%s.jpg" % str(int(time.time()*1000)) )
			print("image captured:", int(time.time()*1000))

			# display the ui to show that the image was taken
			disp.LCD_ShowImage(ui, 0, 0)

		# show preview image on screen
		else:
			cam.resolution = (128,128)
			cam.rotation = 180
			cam.capture("/home/pi/pi_camera/preview.jpg")

			preview = Image.open("preview.jpg")
			disp.LCD_ShowImage(preview, 0, 0)

if __name__ == "__main__":
	try:
		draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
		disp.LCD_ShowImage(ui, 0, 0)

		cam = pc.PiCamera()

		main(ui, cam)

#	except:
#		print("ERROR")

	finally:
		cam.close()

		GPIO.cleanup()
		print(" -GPIO.cleanup()")

		print("\n####################")
		print("#                  #")
		print("#  Program closed  #")
		print("#                  #")
		print("####################")
