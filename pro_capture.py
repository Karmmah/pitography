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

# button mapping (mirrored to references given above)
key3_pin = 16
key2_pin = 20
key1_pin = 21
up_pin = 19
down_pin = 6
left_pin = 26
right_pin = 5
press_pin = 13
backlight_pin = 24

def main(cam):
	ui_width, ui_height = 128, 128
	button_press_wait_time = 0.2

	# GPIO init
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(key3_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(key2_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(key1_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(up_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(down_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(left_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(right_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(press_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(backlight_pin, GPIO.OUT, initial=1)

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
	capture_success_screen_draw.text( (32,60), "Image saved" )
	capture_success_screen = capture_success_screen.rotate(180)

	# create menu screen
	main_menu_screen = Image.new("RGB", (ui_width,ui_height))
	main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
	main_menu_screen_draw.rectangle( (0,0,ui_width,ui_height), fill= 0xffab32)
	#arrows
	main_menu_screen_draw.polygon( (59,58,69,58,64,53), fill=0x000000)
	main_menu_screen_draw.polygon( (70,59,70,69,75,64), fill=0x000000)
	main_menu_screen_draw.polygon( (59,70,69,70,64,75), fill=0x000000)
	main_menu_screen_draw.polygon( (58,59,58,69,53,64), fill=0x000000)
	#labels
	main_menu_screen_draw.text((11,58), " Photo")
	main_menu_screen_draw.text((32,30), " Timelapse")
#	main_menu_screen_draw.line((22,71,40,71), fill=0x00ff00, width=3)
#	main_menu_screen_draw.line((46,43,82,43), fill=0x0000ff, width=3)
	main_menu_screen = main_menu_screen.rotate(180)
	menu_index = 0 #0: no menu, 1: main menu, 2: still photo, 21: still photo settings, 3: timelapse , 31:timelapse interval settings

	capture_mode = 0 #0: still photo, 1: timelapse
	timelapse_capture_flag = False
	timelapse_interval = 5 #[s]
	last_timelapse_frame_time = 0

	main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)

	# main loop
	while True:
		# show menu
		if GPIO.input(key1_pin) == 0 and not timelapse_capture_flag:
			menu_index = 1 if menu_index == 0 else 0
			time.sleep(button_press_wait_time)

		if menu_index != 0:
			#main menu
			if menu_index == 1:
				active_color, inactive_color = 0x0000ff, 0xffab32
#				active_color, inactive_color = 0x00ff00, 0x0000ff
				main_menu_screen_draw.line((106,56,88,56), fill=active_color if capture_mode == 0 else inactive_color, width=3)
				main_menu_screen_draw.line((46,83,82,83), fill=active_color if capture_mode == 1 else inactive_color, width=3)
				disp.LCD_ShowImage(main_menu_screen, 0, 0)
				if GPIO.input(up_pin) == 0:
					capture_mode = 1
				elif GPIO.input(left_pin) == 0:
					capture_mode = 0

			#still photo menu
			elif menu_index == 2:
				pass

			#timelapse menu
			elif menu_index == 3:
				pass

			continue #skip capturing and preview while in menu

		# change magnification
		if GPIO.input(key3_pin) == 0:
			magnify_flag = not magnify_flag
			if magnify_flag:
				cam.zoom = magnify_zoom
			else:
				cam.zoom = (0,0,1,1)
			time.sleep(button_press_wait_time)

		# capture timelapse
		if GPIO.input(press_pin) == 0 and capture_mode == 1:
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
		if GPIO.input(press_pin) == 0 and capture_mode == 0:
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

