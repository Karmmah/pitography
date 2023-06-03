#!/bin/python3

import picamera2
import LCD_Config, LCD_1in44
import RPi.GPIO
import PIL
import io
import traceback
import time

import screens

#available keys on waveshare 1.44in LCD HAT
#PIN 	Raspberry Pi Interface (BCM) 	Description
#KEY1 			P21 		KEY1GPIO
#KEY2 			P20 		KEY2GPIO
#KEY3 			P16 		KEY3GPIO
#Joystick UP 		P6 		Upward direction of the Joystick
#Joystick Down 		P19 		Downward direction of the Joystick
#Joystick Left 		P5 		Left direction of the Joystick
#Joystick Right 	P26 		Right direction of the Joystick
#Joystick Press 	P13 		Press the Joystick
#SCLK 			P11/SCLK 	SPI clock line
#MOSI 			P10/MOS 	SPI data line
#CS 			P8/CE0 		Chip selection
#DC 			P25 		Data/Command control
#RST 			P27 		Reset
#BL 			P24		Backlight

# button mapping (mirrored to references given above)
key1_pin = 21
key2_pin = 20
key3_pin = 16
up_pin = 19
down_pin = 6
left_pin = 26
right_pin = 5
press_pin = 13
backlight_pin = 24

def check_input():
	if GPIO.input(key1_pin) == 0:
		return 21
	elif GPIO.input(key2_pin) == 0:
		return 20
	elif GPIO.input(key3_pin) == 0:
		return 16
	elif GPIO.input(up_pin) == 0:
		return 19
	elif GPIO.input(down_pin) == 0:
		return 6
	elif GPIO.input(left_pin) == 0:
		return 26
	elif GPIO.input(right_pin) == 0:
		return 5
	elif GPIO.input(press_pin) == 0:
		return 13
	else:
		return 0

def main(cam, disp, preview_config, capture_config):
	main_menu_index = 1
	current_menu_index = 0

#	while True:
	for i in range(200): #debug
		# show menu
		pass

		# change magnification
		pass

		# capture still image
		pass

		# capture timelapse
		pass

		# show preview
		preview_array = cam.capture_array()
		preview = PIL.Image.fromarray(preview_array)
		disp.LCD_ShowImage(preview, 0, 0)

	main_menu_screen_draw = PIL.ImageDraw.Draw(screens.main_menu_screen) #debug
	main_menu_screen_draw.line((20,20,100,100), fill=0x00ff00, width=5) #debug
	disp.LCD_ShowImage(screens.main_menu_screen, 0, 0) #debug
	time.sleep(2) #debug

if __name__ == "__main__":
	# set up hardware
	print("setting up GPIO")
	RPi.GPIO.setmode(RPi.GPIO.BCM)
#	RPi.GPIO.setwarnings(False)
	RPi.GPIO.setup(key3_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(key2_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(key1_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(up_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(down_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(left_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(right_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(press_pin, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
	RPi.GPIO.setup(backlight_pin, RPi.GPIO.OUT, initial=1)

	print("setting up display")
	disp = LCD_1in44.LCD()
	Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
	disp.LCD_Init(Lcd_ScanDir)
#	disp.LCD_Clear()
	disp.LCD_ShowImage(screens.startup_screen, 0, 0)

	print("setting up camera")
	cam = picamera2.Picamera2()
	preview_config = cam.create_preview_configuration(main={"size":(128,128)})
	capture_config = cam.create_still_configuration()
	cam.configure(preview_config)
	cam.start()

	try:
		main(cam, disp, preview_config, capture_config)
	except Exception as e:
		print(traceback.format_exc())

	print("camera64 is shutting down")
	cam.stop()
	cam.close()
	disp.LCD_Clear()
	RPi.GPIO.cleanup()

	print("camera64 stopped")
