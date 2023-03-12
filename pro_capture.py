#!/bin/python3

import numpy, time, subprocess

import LCD_1in44, LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
import picamera

#available keys
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

# button mapping
shutter_pin = 13
backlight_pin = 24
magnify_pin = 16
menu_pin = 21

def main(cam):
	ui_width, ui_height = 128, 128
	button_press_wait_time = 0.2

	# GPIO init
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(shutter_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(backlight_pin, GPIO.OUT, initial=1)
	GPIO.setup(magnify_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(menu_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	# display with hardware SPI
	disp = LCD_1in44.LCD()
	Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
	disp.LCD_Init(Lcd_ScanDir)
	disp.LCD_Clear()

	# create and display startup image
	startup_screen = Image.new("RGB", (ui_width,ui_height))
	startup_screen_draw = ImageDraw.Draw(startup_screen)
	startup_screen_draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
	disp.LCD_ShowImage(startup_screen, 0, 0)

	# initialise camera parameters
	max_shutter_time = 20000 #1/50 seconds = 20000µs
	capture_resolution = (4056,3040)
#	capture_resolution = (4032,3040)
	preview_resolution = (ui_width,ui_height)
	magnify_zoom = (0.35, 0.35, 0.3, 0.3)
	magnify_flag = False

	# set up camera
	cam.resolution = preview_resolution
	cam.rotation = 180 #rotation for preview only

	# create capture success screen
	capture_success_screen = Image.new("RGB", (ui_width,ui_height))
	capture_success_screen_draw = ImageDraw.Draw(capture_success_screen)
	capture_success_screen_draw.rectangle( (0,0,ui_width,ui_height), fill=0 )
	capture_success_screen_draw.text( (0,0), "Image saved" )
	capture_success_screen = capture_success_screen.rotate(180)

	# create menu screen
	main_menu_screen = Image.new("RGB", (ui_width,ui_height))
	main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
	main_menu_screen_draw.rectangle( (0,0,ui_width,ui_height), fill= 0xffab32)
	main_menu_screen_draw.polygon( (59,58,69,58,64,53), fill=0x000000)
	main_menu_screen_draw.polygon( (70,59,70,69,75,64), fill=0x000000)
	main_menu_screen_draw.polygon( (59,70,69,70,64,75), fill=0x000000)
	main_menu_screen_draw.polygon( (58,59,58,69,53,64), fill=0x000000)
	main_menu_screen_draw.text((49,30), "Photo")
	main_menu_screen_draw.text((83,58), "TMLPSE")
	main_menu_screen = main_menu_screen.rotate(180)
	menu_index = 0 #0: no menu, 1: main menu, 11: still photo settings, 2: timelapse , 21:timelapse interval settings

	capture_mode = 0 #0: still photo, 1: timelapse
	timelapse_capture_flag = False
	timelapse_interval = 5 #[s]
	last_timelapse_frame_time = 0

	# main loop
	while True:
		# show menu
		if GPIO.input(menu_pin) == 0 and not timelapse_capture_flag:
			menu_index = 1 if menu_index == 0 else 0
			time.sleep(button_press_wait_time)
		if menu_index != 0:
			if menu_index == 1: #main menu
				print("main menu with colors")
#				active_color, inactive_color = 0x00ff00, 0xffab32
				active_color, inactive_color = 0x00ff00, 0xff0000
#				main_menu_screen_draw.line((53,37,75,37), fill=active_color if capture_mode == 0 else inactive_color, width=5)
				main_menu_screen_draw.rectangle((9,7,75,79), fill=0xffffff)
#				main_menu_screen_draw.line((86,65,98,65), fill=active_color if capture_mode == 1 else inactive_color, width=5)
			disp.LCD_ShowImage(main_menu_screen, 0, 0)
			continue #skip capturing and preview while in menu

		# change magnification
		if GPIO.input(magnify_pin) == 0:
			magnify_flag = not magnify_flag
			if magnify_flag:
				cam.zoom = magnify_zoom
			else:
				cam.zoom = (0,0,1,1)
			time.sleep(button_press_wait_time)

		# capture timelapse
		if GPIO.input(shutter_pin) == 0 and capture_mode == 1:
			timelapse_capture_flag = not timelapse_capture_flag
			time.sleep(button_press_wait_time)
		if timelapse_capture_flag:
			if time.time() > last_timelapse_frame_time + timelapse_interval:
				GPIO.output(backlight_pin, 0)
				cam.zoom = (0,0,1,1)
				cam.rotation = 0
				cam.resolution = capture_resolution
				cam.capture("/home/pi/DCIM/timelapse/%d.jpg" & int(time.time()*1000), use_video_port=False)
				cam.resolution = preview_resolution
				cam.rotation = 180
				GPIO.output(backlight_pin, 1)

		# capture still image
		if GPIO.input(shutter_pin) == 0 and capture_mode == 0:
			GPIO.output(backlight_pin, 0) #blank backlight to show image was taken
			# set camera to capture settings
			cam.zoom = (0,0,1,1)
			magnify_flag = False
			cam.rotation = 0
			cam.resolution = capture_resolution
			if cam.exposure_speed > max_shutter_time:
				cam.shutter_speed = max_shutter_time
			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000), use_video_port=False )
			disp.LCD_ShowImage(capture_success_screen, 0, 0)
			# reset camera settings to preview
			cam.shutter_speed = 0 #automatic mode
			cam.resolution = preview_resolution
			cam.rotation = 180
			GPIO.output(backlight_pin, 1)

		# update preview
		overlay = Image.new("L", (ui_width,ui_height))
		ov_draw = ImageDraw.Draw(overlay)
		data = numpy.empty( (preview_resolution[0],preview_resolution[1],3), dtype=numpy.uint8)
		cam.capture(data, "rgb", use_video_port=True)
		preview = Image.fromarray(data, "RGB")
		#draw magnifying glass symbol to overlay
		if magnify_flag:
			ov_draw.ellipse( (98,20,108,30), fill=0xffffff )
			ov_draw.line( (103,25,93,35), fill=0xffffff, width=3 )
		#add current camera info to preview
		ag = cam.analog_gain.numerator / cam.analog_gain.denominator
		dg = cam.digital_gain.numerator / cam.digital_gain.denominator
		s = str(int(1000000/cam.exposure_speed)) if cam.exposure_speed < max_shutter_time else str(int(1000000/max_shutter_time))
		ov_draw.text( (54,3), "pro", fill=0xffffff )
		ov_draw.text( (3,10), "ag "+str(round(ag,1)), fill=0xffffff )
		ov_draw.text( (3,20), "dg "+str(round(dg,1)), fill=0xffffff )
		ov_draw.text( (3,30), "e 1/"+str(int(1000000/cam.exposure_speed)), fill=0xffffff )
		ov_draw.text( (3,40), "s 1/"+s, fill=0xffffff )
		ov_draw.text( (3,50), "i "+(str(cam.iso) if cam.iso != 0 else "auto"), fill=0xffffff )
	#	ov_draw.text( (3,60), "comp "+str(cam.exposure_compensation), fill=0xffffff )
		#check if internet connection is available and displey the cameras ip address
		ov_draw.text( (25,115), text=subprocess.check_output("hostname -I", text=True, shell=True)[:13], fill=0xffffff)
		overlay = overlay.rotate(180)
		preview.paste(ImageOps.colorize(overlay, (0,0,0), (255,255,255)), (0,0), overlay)
		disp.LCD_ShowImage(preview, 0, 0)

if __name__ == "__main__":
	try:
		cam = picamera.PiCamera(framerate=24)
		main(cam)
	finally:
		cam.close()
		print("\nClosed camera")
		GPIO.output(backlight_pin, 0)
		print("Disabled backlight")
		GPIO.cleanup()
		print("GPIO cleanup")
		print("\nPro Capture closed")

