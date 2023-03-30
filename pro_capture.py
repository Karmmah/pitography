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
key1_pin = 21
key2_pin = 20
key3_pin = 16
up_pin = 19
down_pin = 6
left_pin = 26
right_pin = 5
press_pin = 13
backlight_pin = 24

ui_width, ui_height = 128, 128

def main(cam, disp):
	# camera parameters initialisation
	max_shutter_time = 20000 #1/50 seconds = 20000µs
	capture_resolution = (4056,3040)
	preview_resolution = (ui_width,ui_height)
	magnify_zoom = (0.35, 0.35, 0.3, 0.3)
	magnify_flag = False
	button_press_wait_time = 0.2

	# camera setup
	cam.resolution = preview_resolution
	cam.rotation = 180 #rotation for preview

	# capture success screen setup
	capture_success_screen = Image.new("RGB", (ui_width,ui_height))
	capture_success_screen_draw = ImageDraw.Draw(capture_success_screen)
	capture_success_screen_draw.rectangle( (0,0,ui_width,ui_height), fill=0 )
	capture_success_screen_draw.text( (32,60), "Image saved" )
	capture_success_screen = capture_success_screen.rotate(180)

	# menu screen setup
	current_menu_index = 0
	main_menu_index = 1
	main_menu_screen = Image.new("RGB", (ui_width,ui_height))
	main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
	main_menu_screen_draw.rectangle( (0,0,ui_width,ui_height), fill= 0xd89552)
	#arrows
	main_menu_screen_draw.polygon( (59,58,69,58,64,53), fill=0x000000)
	main_menu_screen_draw.polygon( (70,59,70,69,75,64), fill=0x000000)
	main_menu_screen_draw.polygon( (59,70,69,70,64,75), fill=0x000000)
	main_menu_screen_draw.polygon( (58,59,58,69,53,64), fill=0x000000)
	#labels
	main_menu_screen_draw.text((11,58), " Photo")
	main_menu_screen_draw.text((32,30), " Timelapse")
	main_menu_screen = main_menu_screen.rotate(180)

	# still menu setup
	still_menu_index = 2
	still_menu_screen = Image.new("RGB", (ui_width,ui_height))
	still_menu_draw = ImageDraw.Draw(still_menu_screen)
	still_menu_draw.rectangle((0,0,ui_width,ui_height), fill=0x0000a9)
	still_menu_draw.text((16,8), " Photo Settings")
	still_menu_screen = still_menu_screen.rotate(180)

	# timelapse menu setup
	timelapse_menu_index = 3
	interval_options = [2,4,6,10] #[s]
	timelapse_interval_index = 1
	timelapse_menu_screen = Image.new("RGB", (ui_width,ui_height))
	timelapse_menu_draw = ImageDraw.Draw(timelapse_menu_screen)
	timelapse_menu_draw.rectangle((0,0,ui_width,ui_height), fill=0x007000)
	timelapse_menu_draw.text((5,8), " Timelapse Settings")
	timelapse_menu_draw.text((21,30), " Interval")

	current_capture_mode = 0
	still_capture_index = 0
	timelapse_capture_index = 1
	timelapse_capture_flag = False
	last_timelapse_frame_time = 0
	last_timelapse_exposure_times = [] #save exposure times of the last photos taken to smooth out exposure

	# reassign draw objects to menu screens after rotation (otherwise it cannot be drawn to again)
	main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
#	still_menu_draw = ImageDraw.Draw(still_menu_screen)
	timelapse_menu_draw = ImageDraw.Draw(timelapse_menu_screen)

	# main loop
	while True:
		timelapse_interval = interval_options[timelapse_interval_index]

		# show or hide menu
		if GPIO.input(key1_pin) == 0 and not timelapse_capture_flag:
			current_menu_index = main_menu_index if current_menu_index == 0 else 0
			time.sleep(button_press_wait_time)

		if current_menu_index != 0:
			#main menu
			if current_menu_index == main_menu_index:
#				active_color, inactive_color = 0x0000ff, 0xffab32
				active_color, inactive_color = 0x0000ff, 0xd89552
#				active_color, inactive_color = 0x00ff00, 0x0000ff
				main_menu_screen_draw.line((106,56,88,56), fill = active_color if current_capture_mode == still_capture_index else inactive_color, width=3)
				main_menu_screen_draw.line((46,83,82,83), fill = active_color if current_capture_mode == timelapse_capture_index else inactive_color, width=3)
				disp.LCD_ShowImage(main_menu_screen, 0, 0)

				if GPIO.input(up_pin) == 0:
					current_capture_mode = timelapse_capture_index
					current_menu_index = timelapse_menu_index
					time.sleep(button_press_wait_time)
				elif GPIO.input(left_pin) == 0:
					current_capture_mode = still_capture_index
					current_menu_index = still_menu_index
					time.sleep(button_press_wait_time)

			#still photo menu
			elif current_menu_index == still_menu_index:
				if GPIO.input(press_pin) == 0:
					current_menu_index = 0
					time.sleep(button_press_wait_time)
				disp.LCD_ShowImage(still_menu_screen, 0, 0)

			#timelapse menu
			elif current_menu_index == timelapse_menu_index:
				if GPIO.input(press_pin) == 0:
					current_menu_index = 0
					time.sleep(button_press_wait_time)
				if GPIO.input(left_pin) == 0:
					if timelapse_interval_index <= 0:
						pass
					else:
						timelapse_interval_index -= 1
				if GPIO.input(right_pin) == 0:
					if timelapse_interval_index >= len(interval_options)-1:
						pass
					else:
						timelapse_interval_index += 1
				timelapse_menu_draw.rectangle((83,31,96,39), fill=0x007000)
				timelapse_menu_draw.text((84,30), text=str(interval_options[timelapse_interval_index]))
				rotated_screen = timelapse_menu_screen.rotate(180)
				disp.LCD_ShowImage(rotated_screen, 0, 0)

			time.sleep(0.1)
			continue #skip image capture and preview while in menu

		# change magnification
		if GPIO.input(key3_pin) == 0:
			magnify_flag = not magnify_flag
			if magnify_flag:
				cam.zoom = magnify_zoom
			else:
				cam.zoom = (0,0,1,1)
			time.sleep(button_press_wait_time)

		# capture timelapse
		if GPIO.input(press_pin) == 0 and current_capture_mode == timelapse_capture_index:
			timelapse_capture_flag = not timelapse_capture_flag
			time.sleep(button_press_wait_time)
		if timelapse_capture_flag:
			if time.time() > (last_timelapse_frame_time + timelapse_interval):
				GPIO.output(backlight_pin, 0)
				if len(last_timelapse_exposure_times) < 10:
					last_timelapse_exposure_times += [cam.exposure_speed]
				else:
					last_timelapse_exposure_times = last_timelapse_exposure_times[0:9]+[cam.exposure_speed]
					avg_exposure = int(round((last_timelapse_exposure_times[0]+last_timelapse_exposure_times[1]+last_timelapse_exposure_times[2]+last_timelapse_exposure_times[3]+last_timelapse_exposure_times[4]+last_timelapse_exposure_times[5]+last_timelapse_exposure_times[6]+last_timelapse_exposure_times[7]+last_timelapse_exposure_times[8]+last_timelapse_exposure_times[9])/10, 0))
					cam.shutter_speed = avg_exposure
				cam.zoom = (0,0,1,1)
				cam.rotation = 0
				cam.resolution = capture_resolution
				cam.capture("/home/pi/DCIM/timelapse/%d.jpg" % int(time.time()*1000), use_video_port=False)
				last_timelapse_frame_time = time.time()
				cam.resolution = preview_resolution
				cam.rotation = 180
				cam.shutter_speed = 0 #0: automatic mode
				GPIO.output(backlight_pin, 1)

		# capture still image
		if GPIO.input(press_pin) == 0 and current_capture_mode == still_capture_index:
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
			cam.shutter_speed = 0 #0: automatic mode
			cam.resolution = preview_resolution
			cam.rotation = 180
			GPIO.output(backlight_pin, 1)

		# update preview
		overlay = Image.new("L", (ui_width,ui_height))
		overlay_draw = ImageDraw.Draw(overlay)
		data = numpy.empty( (preview_resolution[0],preview_resolution[1],3), dtype=numpy.uint8)
		cam.capture(data, "rgb", use_video_port=True)
		preview = Image.fromarray(data, "RGB")
		if magnify_flag:
			#draw magnifying glass symbol to overlay
			overlay_draw.ellipse( (98,20,108,30), fill=0xffffff )
			overlay_draw.line( (103,25,93,35), fill=0xffffff, width=3 )
		#add current camera info to preview
		ag = cam.analog_gain.numerator / cam.analog_gain.denominator
		dg = cam.digital_gain.numerator / cam.digital_gain.denominator
		s = str(int(1000000/cam.exposure_speed)) if cam.exposure_speed < max_shutter_time else str(int(1000000/max_shutter_time))

		overlay_draw.text( (3,18), "ag "+str(round(ag,1)), fill=0xffffff )
		overlay_draw.text( (3,28), "dg "+str(round(dg,1)), fill=0xffffff )
		overlay_draw.text( (3,38), "e 1/"+str(int(1000000/cam.exposure_speed)), fill=0xffffff )
		overlay_draw.text( (3,48), "s 1/"+s, fill=0xffffff )
		overlay_draw.text( (3,58), "i "+(str(cam.iso) if cam.iso != 0 else "auto"), fill=0xffffff )
		if current_capture_mode == still_capture_index:
			overlay_draw.text( (1,1), " Photo", fill=0xffffff )
			overlay_draw.text( (0,0), " Photo", fill=0xffffff )
		elif current_capture_mode == timelapse_capture_index:
			overlay_draw.text( (1,1), " Timelapse", fill=0xffffff )
			overlay_draw.text( (0,0), " Timelapse", fill=0xffffff )
			overlay_draw.text( (44,12), " Interval %ds" % timelapse_interval, fill=0xffffff)
			if timelapse_capture_flag:
				overlay_draw.text( (9,80), "Capturing Timelapse", fill=0xffffff )
				time.sleep(0.5) #reduce preview rate to reduce power consumption during timelapse recording
		#check if internet connection is available and displey the cameras ip address
		connection_status = subprocess.check_output("hostname -I", text=True, shell=True)[:13]
		overlay_draw.text( (27,115), text= connection_status if connection_status != "" else "no connection", fill=0xffffff)
		overlay = overlay.rotate(180)
#		preview.paste(ImageOps.colorize(overlay, (0,0,0), (255,240,0)), (0,0), overlay)
		preview.paste(ImageOps.colorize(overlay, (0,0,0), (155,155,155)), (0,0), overlay)
#		preview.paste(ImageOps.colorize(overlay, (0,0,0), (255,255,255)), (0,0), overlay)
		disp.LCD_ShowImage(preview, 0, 0)

# program start
if __name__ == "__main__":
	try:
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

		cam = picamera.PiCamera(framerate=24)

		# display with hardware SPI setup
		disp = LCD_1in44.LCD()
		Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
		disp.LCD_Init(Lcd_ScanDir)
		disp.LCD_Clear()

		# startup image creation and display
		startup_screen = Image.new("RGB", (ui_width,ui_height))
		startup_screen_draw = ImageDraw.Draw(startup_screen)
		startup_screen_draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
		disp.LCD_ShowImage(startup_screen, 0, 0)

		main(cam, disp)

	finally:
		cam.close()
		print("\nClosed camera")
		GPIO.output(backlight_pin, 0)
		print("Disabled backlight")
		disp.LCD_Clear()
		print("Cleared display")
		GPIO.cleanup()
		print("GPIO cleanup")
		print("\nPro Capture closed")

