#!/bin/python3

import picamera2, libcamera
import LCD_Config, LCD_1in44
import RPi.GPIO
import PIL
from PIL import ImageOps
import io
import traceback
import time
import subprocess

import screens

#available keys on waveshare 1.44in LCD HAT
#PIN 	Raspberry Pi Interface (BCM) 	Description
#KEY1				P21			KEY1GPIO
#KEY2				P20			KEY2GPIO
#KEY3				P16			KEY3GPIO
#Joystick UP		P6			Upward direction of the Joystick
#Joystick Down		P19			Downward direction of the Joystick
#Joystick Left		P5			Left direction of the Joystick
#Joystick Right		P26			Right direction of the Joystick
#Joystick Press		P13			Press the Joystick
#SCLK				P11/SCLK	SPI clock line
#MOSI				P10/MOS		SPI data line
#CS					P8/CE0		Chip selection
#DC					P25			Data/Command control
#RST				P27			Reset
#BL					P24			Backlight

# button mapping (mirrored to references given above)
key1_pin		= 21
key2_pin		= 20
key3_pin		= 16
up_pin			= 19
down_pin		= 6
left_pin		= 26
right_pin		= 5
press_pin		= 13
backlight_pin	= 24


red		= 0x0000ff
white	= 0xffffff
black	= 0x000000


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
	timelapse_capture_flag = False
	last_timelapse_frame_time = 0
	last_timelapse_exposure_times = [] #save exposure times of the last photos taken to smooth out exposure
	timelapse_start_str = "no_timelapse_started"
	timelapse_frame_nr = 0

	timelapse_interval = 5 #temporary, change when timelapse menu is implemented

	current_capture_mode = still_capture_index #default value

	button_hold_flag = False
	magnify_flag = False

	last_input_time = time.time()
	energy_saving_flag = False

	main_menu_screen_draw = PIL.ImageDraw.Draw(screens.main_menu_screen)

	overlay = PIL.Image.new("L", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
	overlay_draw = PIL.ImageDraw.Draw(overlay)
	rotated_overlay = overlay.rotate(180)

	i = 0
	while True:
		i = i+1 if i < 100 else 0

		input_key = check_input()
		if input_key != 0:
			last_input_time = time.time()

		if time.time() - last_input_time > 30:
			energy_saving_flag = True
		else:
			energy_saving_flag = False

		# check if button is held
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
			main_menu_screen_draw.line((106,56,88,56), width=2, fill=red if current_capture_mode == still_capture_index else white)
			main_menu_screen_draw.line((46,83,82,83), width=2, fill=red if current_capture_mode == timelapse_capture_index else white)
			disp.LCD_ShowImage(screens.main_menu_screen, 0, 0)
			time.sleep(0.4)
			input_key = 0
			while input_key == 0:
				input_key = check_input()
				time.sleep(0.033)
			if input_key == key1_pin or input_key == press_pin:
				current_menu_index = 0
			if input_key == down_pin:
				continue
			elif input_key == left_pin:
				current_capture_mode = still_capture_index
				current_menu_index = 0
			elif input_key == up_pin:
				current_capture_mode = timelapse_capture_index
				current_menu_index = 0
			elif input_key == right_pin: #exit program
				print("manual shutdown")
				subprocess.run("sudo shutdown now", shell=True, text=True)
				return
			continue

		# change magnification
		if input_key == key3_pin:
			magnify_flag = not magnify_flag
			if magnify_flag == True:
				picam2.set_controls({"ScalerCrop": (1572,1064,912,912)})
			else:
				picam2.set_controls({"ScalerCrop": (508,0,3040,3040)})

		# capture still image
		if current_capture_mode == still_capture_index and input_key == press_pin:
			print("[!] capture start")
			#RPi.GPIO.output(backlight_pin, 0)
			magnify_flag = False
			image_name = time.strftime("%Y%m%d_%H%M%S")
			#picam2.switch_mode_and_capture_file(capture_config, "/home/pi/DCIM/%d.jpg" % image_name)
			picam2.stop()
			picam2.configure(capture_config)
			error = 1
			while error > 0:
				try:
					picam2.start()
					picam2.capture_file(f'/home/pi/DCIM/{image_name}.jpg', format="jpeg")
					error = 0
				except Exception as err:
					print(f"\t[!] error #{error}:{err}\n\tretrying")
					picam2.stop()
					error += 1
			picam2.stop()
			picam2.configure(preview_config)
			picam2.start()
			print(f"[!] captured {image_name}.jpg")
			disp.LCD_ShowImage(screens.capture_screen, 0, 0)
			#RPi.GPIO.output(backlight_pin, 1)
			last_input_time = time.time() #avoid energy saving after capture

		# capture timelapse
		if current_capture_mode == timelapse_capture_index and input_key == press_pin:
			timelapse_capture_flag = not timelapse_capture_flag
			if timelapse_capture_flag == True:
				timelapse_start_str = time.strftime("%Y%m%d_%H%M%S")
				timelapse_frame_nr = 1
			print(f"[#] DEBUG timelapse capture: timelapse_capture_flag:{timelapse_capture_flag}")
		if timelapse_capture_flag:
			if time.time() > (last_timelapse_frame_time + timelapse_interval):
				RPi.GPIO.output(backlight_pin, 0)
				#if len(last_timelapse_exposure_times) < 10:
				#	last_timelapse_exposure_times += [picam2.exposure_speed]
				#else:
				#	last_timelapse_exposure_times = last_timelapse_exposure_times[0:9]+[picam2.exposure_speed]
				#	avg_exposure = int(round((last_timelapse_exposure_times[0]+last_timelapse_exposure_times[1]+last_timelapse_exposure_times[2]+last_timelapse_exposure_times[3]+last_timelapse_exposure_times[4]+last_timelapse_exposure_times[5]+last_timelapse_exposure_times[6]+last_timelapse_exposure_times[7]+last_timelapse_exposure_times[8]+last_timelapse_exposure_times[9])/10, 0))
				#	#picam2.shutter_speed = avg_exposure
				#	picam2.set_controls({"ExposureTime": avg_exposure})
				frame_nr_str = "%4d" % timelapse_frame_nr
				frame_nr_str = frame_nr_str.replace(" ", "0")
				image_name = f"{timelapse_start_str}_{frame_nr_str}"
				picam2.stop()
				picam2.configure(capture_config)
				picam2.start()
				picam2.capture_file(f'/home/pi/DCIM/timelapse/{image_name}.jpg')
				timelapse_frame_nr += 1
				last_timelapse_frame_time = time.time()
				picam2.stop()
				picam2.configure(preview_config)
				picam2.start()
				print(f"[!] captured {image_name}.jpg")
				RPi.GPIO.output(backlight_pin, 1)

		# show preview
		#create overlay
		if energy_saving_flag == True and i%5 != 0:
			time.sleep(0.1)
			continue
		if i%5 == 0:
			overlay_draw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=black)
			#add capture mode to overlay
			if current_capture_mode == timelapse_capture_index:
				overlay_draw.text( (1,1), " Timelapse", fill=white ) #drop shadow like to make it look nicer
				overlay_draw.text( (0,0), " Timelapse", fill=white )
				overlay_draw.text( (72,0), f"{timelapse_interval}s", fill=white)
				if timelapse_capture_flag:
					overlay_draw.text( (36,14), "capturing", fill=white )
					time.sleep(0.2) #reduce preview rate to reduce power consumption during timelapse recording
			else:
				overlay_draw.text( (1,1), " Photo", fill=white ) #drop shadow like to make it look nicer
				overlay_draw.text( (0,0), " Photo", fill=white )
			#add capture parameters to overlay
			metadata = picam2.capture_metadata()
			overlay_draw.text((3,27), "prev", fill=white)
			overlay_draw.text((3,58), "-", fill=white)
			overlay_draw.text((3,87), "menu", fill=white)
			overlay_draw.text((90,18), "ag\n"+str(round(metadata["AnalogueGain"],1)), fill=white)
			overlay_draw.text((90,48), "dg\n"+str(round(metadata["DigitalGain"],1)), fill=white)
			overlay_draw.text((90,78), "e\n1/"+str(int((metadata["ExposureTime"]/1000000)**(-1))), fill=white)
			with open("/sys/class/thermal/thermal_zone0/temp") as f:
				temp = int(int(f.read().rstrip("\n"))/1000)
			overlay_draw.text((3, 114), f"t {str(temp)}", fill=white)
			connection = subprocess.check_output("hostname -I", shell=True, text=True)[:13]
			overlay_draw.text((28,114), f'|{connection if len(connection) >= 4 and connection[3] == "." else "no connection"}', fill=white)
			rotated_overlay = overlay.rotate(180)
		#get preview from camera
		preview_array = picam2.capture_array()
		preview = PIL.Image.fromarray(preview_array)
		#preview.paste(ImageOps.colorize(rotated_overlay, (255,255,255), (0,0,0)), (0,0), rotated_overlay)
		preview.paste(ImageOps.colorize(rotated_overlay, (0,0,0), (255,255,255)), (0,0), rotated_overlay)
		disp.LCD_ShowImage(preview, 0, 0)


if __name__ == "__main__":

	# GPIO setup
	print("[!] setting up GPIO")
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

	# display setup
	print("[!] setting up display")
	disp = LCD_1in44.LCD()
	Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
	disp.LCD_Init(Lcd_ScanDir)
	#disp.LCD_Clear()
	disp.LCD_ShowImage(screens.startup_screen, 0, 0)

	# camera setup
	print("[!] setting up camera")
	picam2 = picamera2.Picamera2()
	capture_config = picam2.create_still_configuration()
	preview_config = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)})
	preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
	#magnify_config = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)})
	#magnify_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
	picam2.configure(preview_config)
	picam2.start()

	#print("Camera Controls:",picam2.camera_controls) #debug
	#print("ScalerCrop:",picam2.camera_controls['ScalerCrop'][2]) #debug
	print(f"[#] DEBUG Capture Metadata:{picam2.capture_metadata()}") #['ScalerCrop'][2:]) #debug

	try:
		print("[!] starting main method")
		main(picam2, disp, preview_config, capture_config)
	except Exception as e:
		print(traceback.format_exc())

	print("[!] camera64 is shutting down")
	picam2.stop()
	picam2.close()
	disp.LCD_Clear()
	RPi.GPIO.cleanup()

	print("[!] camera64 stopped")
