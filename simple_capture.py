import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO

import time
import picamera as pc

# button mapping
shutter_pin = 13
backlight_pin = 24
magnify_pin = 21

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
GPIO.setup(shutter_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(backlight_pin, GPIO.OUT, initial=1)
GPIO.setup(magnify_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def main(ui, cam):
	draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
	disp.LCD_ShowImage(ui, 0, 0)

	ui.rotate(180)

	magnify_flag = False

	print("Running the program loop")
	while True:
		# capture image
		if GPIO.input(shutter_pin) == 0:
			# blank the backlight to visualise that the image was taken
			GPIO.output(backlight_pin, 0)

#			cam.resolution = (4056,3040)
			cam.resolution = (4056,2028)
#			cam.resolution = (2028,1520)
			cam.rotation = 0
			cam.zoom = (0,0,1,1)

#			cam.capture( "/home/pi/DCIM/%s.jpg" % str(int(time.time()*1000)) )
			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000) )
			print("image captured:", int(time.time()*1000))

			GPIO.output(backlight_pin, 1)

		# show preview image on screen
		else:
			cam.resolution = (128,128)
			cam.rotation = 180

			stream = BytesIO()
			cam.capture(stream, format="jpeg")
			stream.seek(0)
			preview = Image.open(stream)

			if magnify_flag:
				magnify_icon = ImageDraw.Draw(preview)
				magnify_icon.rectangle( (10,20,20,30), fill=0xffffff )
				magnify_icon.rectangle( (13,10,17,20), fill=0xffffff )

			disp.LCD_ShowImage(preview, 0, 0)

		# check if maginfy button is pressed
		if GPIO.input(magnify_pin) == 0:
			magnify_flag = not magnify_flag

			if magnify_flag:
				cam.zoom = (0.35,0.35,0.3,0.3)
			else:
				cam.zoom = (0,0,1,1)

if __name__ == "__main__":
	try:
		draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
		disp.LCD_ShowImage(ui, 0, 0)

		cam = pc.PiCamera()
		time.sleep(2)
		cam.zoom = (0,0,1,1) #reset camera crop
		cam.start_preview() #preview to adjust exposure to available light

		main(ui, cam)

#	except:
#		print("ERROR")

	finally:
		cam.stop_preview()
		cam.close()

		GPIO.cleanup()
		print(" -GPIO.cleanup()")

		print("\n####################")
		print("#                  #")
		print("#  Program closed  #")
		print("#                  #")
		print("####################")
