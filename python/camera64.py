#!/bin/python3

import picamera2, libcamera
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
	if RPi.GPIO.input(key1_pin) == 0:
		return 21
	elif RPi.GPIO.input(key2_pin) == 0:
		return 20
	elif RPi.GPIO.input(key3_pin) == 0:
		return 16
	elif RPi.GPIO.input(up_pin) == 0:
		return 19
	elif RPi.GPIO.input(down_pin) == 0:
		return 6
	elif RPi.GPIO.input(left_pin) == 0:
		return 26
	elif RPi.GPIO.input(right_pin) == 0:
		return 5
	elif RPi.GPIO.input(press_pin) == 0:
		return 13
	else:
		return 0

def main(picam2, disp, preview_config, capture_config):
	main_menu_index = 1
	current_menu_index = 0

	still_capture_index = 0
	timelapse_capture_index = 1
	current_capture_index = still_capture_index

	button_hold_flag = False
	last_input_time = None

	main_menu_screen_draw = PIL.ImageDraw.Draw(screens.main_menu_screen)

	while True:
#		with open("/sys/class/thermal/thermal_zone0/temp") as f:
#			print(f.read(), end="")

		input_key = check_input()

		if button_hold_flag == True:
			if input_key == 0:
				button_hold_flag = False
			else:
				input_key = 0
		elif input_key != 0:
			last_input_time = time.time()
			button_hold_flag = True
#		print("input key:",input_key,"button hold:",button_hold_flag) #debug

		# show menu
		#main menu
		if current_menu_index == 0 and input_key == key1_pin:
			current_menu_index = main_menu_index
			continue
		elif current_menu_index == main_menu_index:
			if input_key == key1_pin or input_key == press_pin:
				current_menu_index = 0
			if input_key == left_pin:
				current_capture_index = still_capture_index
				current_menu_index = 0
#			elif input_key == up_pin:
#				current_capture_index = timelapse_capture_index
			elif input_key == right_pin: #exit program
				print("manual shutdown")
				return
			main_menu_screen_draw.line((106,56,88,56), width=5, fill=0x0000ff if current_capture_index == still_capture_index else 0xffffff)
			main_menu_screen_draw.line((46,83,82,83), width=5, fill=0x0000ff if current_capture_index == timelapse_capture_index else 0xffffff)
			disp.LCD_ShowImage(screens.main_menu_screen, 0, 0)
			time.sleep(0.05)
			continue

		# change magnification
		pass

		# capture still image
		if input_key == press_pin:
#			RPi.GPIO.output(backlight_pin, 0)

			picam2.switch_mode_and_capture_file(capture_config, "/home/pi/DCIM/%d.jpg" % int(time.time()*1000), format='jpeg')

#			picam2.stop()
#			picam2.configure(capture_config)
#			picam2.start()
#			picam2.capture_file("/home/pi/DCIM/%d.jpg" % int(time.time()*1000))
#			picam2.stop()
#			picam2.configure(preview_config)
#			picam2.start()

#			picam2.capture_file("/home/pi/DCIM/%d.jpg" % int(time.time()*1000))

			disp.LCD_ShowImage(screens.capture_screen, 0, 0)
#			RPi.GPIO.output(backlight_pin, 1)

		# capture timelapse
		pass

		# show preview
		preview_array = picam2.capture_array()
		preview = PIL.Image.fromarray(preview_array)
		disp.LCD_ShowImage(preview, 0, 0)

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
	picam2 = picamera2.Picamera2()
	preview_config = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)})
	preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
	magnify_config = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)})
	magnify_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
	capture_config = picam2.create_still_configuration()
	picam2.configure(preview_config)
	picam2.start()

	try:
		main(picam2, disp, preview_config, capture_config)
	except Exception as e:
		print(traceback.format_exc())

	print("camera64 is shutting down")
	picam2.stop()
	picam2.close()
	disp.LCD_Clear()
	RPi.GPIO.cleanup()

	print("camera64 stopped")
