#!/bin/python3

import picamera2, libcamera
import PIL
from PIL import ImageOps
import io
import traceback
import time
import subprocess

import LCD_Config, LCD_1in44
import RPi.GPIO
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


def run(picam2, disp, preview_config, capture_config):
	currentMenuIndex = 0
	settingsMenuSelectedItem = 0

	still_capture_index = 0
	timelapse_capture_index = 1
	timelapse_capture_flag = False
	last_timelapse_frame_time = 0
	last_timelapse_exposure_times = [] #save exposure times of the last photos taken to smooth out exposure
	timelapseStartStr = "no_timelapse_started"
	timelapse_frame_nr = 0

	timelapse_interval = 5 #temporary, change when timelapse menu is implemented

	currentCaptureMode = still_capture_index #default value

	button_hold_flag = False
	magnify_flag = False

	last_input_time = time.time()
	energySavingFlag = False

	main_menu_screen_draw = PIL.ImageDraw.Draw(screens.main_menu_screen)

	overlay = PIL.Image.new("L", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
	overlayDraw = PIL.ImageDraw.Draw(overlay)
	rotated_overlay = overlay.rotate(180)

	counter = 0 #for doing stuff only every nth update cycle
	while True: #program loop
		counter = counter+1 if counter < 100 else 0

		inputKey = check_input()
		if inputKey != 0:
			last_input_time = time.time()

		if time.time() - last_input_time > 30:
			energySavingFlag = True
		else:
			energySavingFlag = False

		# check if button is held
		if button_hold_flag == True:
			if inputKey == 0:
				button_hold_flag = False
			else:
				inputKey = 0
		elif inputKey != 0:
			last_input_time = time.time()
			button_hold_flag = True
#		print("[!] DEBUG input key:{inputKey} button hold:{button_hold_flag}")

		# show menu
		if currentMenuIndex == 0 and inputKey == key1_pin:
			currentMenuIndex = screens.mainMenuIndex
			continue

		#main menu
		elif currentMenuIndex == screens.mainMenuIndex:
			# draw active capture mode indicator
			main_menu_screen_draw.line((106,56,88,56), width=2, fill=red if currentCaptureMode == still_capture_index else white)
			main_menu_screen_draw.line((46,83,82,83), width=2, fill=red if currentCaptureMode == timelapse_capture_index else white)
			disp.LCD_ShowImage(screens.main_menu_screen, 0, 0)
			inputKey = 0
			while inputKey == 0:
				inputKey = check_input()
				time.sleep(0.1)
			#if inputKey == key1_pin or inputKey == press_pin:
			if inputKey in [press_pin, key2_pin, key3_pin]:
				currentMenuIndex = 0; continue
			elif inputKey == down_pin:
				currentMenuIndex = screens.settingsMenuIndex
			elif inputKey == left_pin:
				currentCaptureMode = still_capture_index
				currentMenuIndex = 0; continue
			elif inputKey == up_pin:
				currentCaptureMode = timelapse_capture_index
				currentMenuIndex = 0; continue
			elif inputKey == right_pin:
				currentMenuIndex = screens.offScreenIndex
			else:
				time.sleep(0.2)
				continue

		#off menu
		elif currentMenuIndex == screens.offScreenIndex:
			disp.LCD_ShowImage(screens.offScreen, 0, 0)
			while inputKey == 0:
				inputKey = check_input()
				time.sleep(0.1)
			if inputKey == left_pin:
				currentMenuIndex = screens.mainMenuIndex
			elif inputKey == up_pin:
				print("[!] shutdown")
				subprocess.run("sudo shutdown now", shell=True, text=True)
				print("[-------shutdown-------]")
				return
			elif inputKey == down_pin:
				print("[!] exit camera")
				return
			else:
				time.sleep(0.2)
				continue

		#off menu
		elif currentMenuIndex == screens.offScreenIndex:
			disp.LCD_ShowImage(screens.offScreen, 0, 0)
			if inputKey == left_pin:
				currentMenuIndex = screens.mainMenuIndex
			elif inputKey == up_pin:
				print("[!] shutdown")
				subprocess.run("sudo shutdown now", shell=True, text=True)
				print("[-------shutdown-------]")
				return
			elif inputKey == down_pin:
				print("[!] exit camera")
				return
			else:
				time.sleep(0.2)
				continue

		#settings menu
		elif currentMenuIndex == screens.settingsMenuIndex:
			if inputKey == press_pin:
				#cam.exposure_mode = exposure_modes[exposure_mode_index]
				currentMenuIndex = 0
			elif inputKey == key1_pin:
				#cam.exposure_mode = exposure_modes[exposure_mode_index]
				currentMenuIndex = 1
			elif inputKey == down_pin:
				settingsMenuSelectedItem += 1 if settingsMenuSelectedItem < 1 else 0
			elif inputKey == up_pin:
				settingsMenuSelectedItem -= 1 if settingsMenuSelectedItem > 0 else 0
			elif inputKey == left_pin and settingsMenuSelectedItem == 0:
				exposure_mode_index -= 1 if exposure_mode_index > 0 else 0
			elif inputKey == right_pin and settingsMenuSelectedItem == 0:
				exposure_mode_index += 1 if settingsMenuSelectedItem < 12 else 0
			elif inputKey == left_pin and settingsMenuSelectedItem == 1:
				shutter_limit_flag = False
#				exposure_mode_index -= 1 if exposure_mode_index > 0 else 0
			elif inputKey == right_pin and settingsMenuSelectedItem == 1:
				shutter_limit_flag = True
#				exposure_mode_index += 1 if settingsMenuSelectedItem < 12 else 0
			# update menu screen
			screens.settingsMenuDraw.rectangle((70,31,128,40), fill=0xd89552) #erase old value
			#screens.settingsMenuDraw.text((70,30), text=exposure_modes[exposure_mode_index], fill=0x00c7ff if settingsMenuSelectedItem == 0 else 0xffffff)
			screens.settingsMenuDraw.text((70,30), text="exposure_modes", fill=0x00c7ff if settingsMenuSelectedItem == 0 else 0xffffff)
			screens.settingsMenuDraw.rectangle((70,48,105,56), fill=0xd89552) #erase old value
			#screens.settingsMenuDraw.text((70,47), text=" %s" % (shutter_limit_flag), fill=0x00c7ff if settingsMenuSelectedItem == 1 else 0xffffff)
			screens.settingsMenuDraw.text((70,47), text="shutter limit", fill=0x00c7ff if settingsMenuSelectedItem == 1 else 0xffffff)

			settingsMenuScreen = screens.settingsMenuScreen.rotate(180)
			disp.LCD_ShowImage(settingsMenuScreen, 0, 0)
			continue

		# change magnification
		if inputKey == key3_pin:
			magnify_flag = not magnify_flag
			if magnify_flag == True:
				picam2.set_controls({"ScalerCrop": (1572,1064,912,912)})
			else:
				picam2.set_controls({"ScalerCrop": (508,0,3040,3040)})

		# capture still image
		if currentCaptureMode == still_capture_index and inputKey == press_pin:
			print("[!] capture start")
			#RPi.GPIO.output(backlight_pin, 0)
			magnify_flag = False
			image_name = time.strftime("%Y%m%d_%H%M%S")
			#picam2.switch_mode_and_capture_file(capture_config, "/home/pi/DCIM/%d.jpg" % image_name)
			picam2.stop(); picam2.configure(capture_config)
			error = 1
			while error != 0:
				try:
					picam2.start()
					picam2.capture_file(f'/home/pi/DCIM/{image_name}.jpg', format="jpeg")
					error = 0
				except Exception as err:
					print(f"\t[!] error #{error}:{err}\n\tretrying")
					picam2.stop()
					error += 1
			picam2.stop(); picam2.configure(preview_config); picam2.start()
			print(f"[!] captured {image_name}.jpg")
			disp.LCD_ShowImage(screens.capture_screen, 0, 0)
			#RPi.GPIO.output(backlight_pin, 1)
			last_input_time = time.time() #avoid energy saving after capture

		# capture timelapse
		#switch timelapse capture on/off
		if currentCaptureMode == timelapse_capture_index and inputKey == press_pin: #start or stop timelapse capture
			timelapse_capture_flag = not timelapse_capture_flag
			if timelapse_capture_flag == True:
				timelapseStartStr = time.strftime("%Y%m%d_%H%M%S")
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
				#	picam2.shutter_speed = avg_exposure
				#	picam2.set_controls({"ExposureTime": avg_exposure})
				timelapseFrameNrStr = "%04d" % timelapse_frame_nr
				image_name = f"{timelapseStartStr}_{timelapseFrameNrStr}"
				picam2.stop(); picam2.configure(capture_config); picam2.start()
				picam2.capture_file(f'/home/pi/DCIM/timelapse/{image_name}.jpg')
				timelapse_frame_nr += 1
				last_timelapse_frame_time = time.time()
				picam2.stop(); picam2.configure(preview_config); picam2.start()
				print(f"[!] captured {image_name}.jpg")
				RPi.GPIO.output(backlight_pin, 1)

		# show preview
		if energySavingFlag == True and counter % 7 != 0: #reduce screen refresh rate in energy save mode
			time.sleep(0.1); continue

		#populate overlay
		if counter % 5 == 0: #update preview every nth cycle
			overlayDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=black)

			#capture mode
			if currentCaptureMode == timelapse_capture_index:
				overlayDraw.text( (1,1), " Timelapse", fill=white ) #drop shadow like to make it look nicer
				overlayDraw.text( (0,0), " Timelapse", fill=white )
				overlayDraw.text( (72,0), f"{timelapse_interval}s", fill=white)
				if timelapse_capture_flag:
					overlayDraw.text( (36,14), "capturing", fill=white )
					#time.sleep(0.2) #reduce preview rate to reduce power consumption during timelapse recording
			elif currentCaptureMode == still_capture_index:
				#overlayDraw.text( (1,1), " Photo", fill=white ) #drop shadow like to make it look nicer
				#overlayDraw.text( (0,0), " Photo", fill=white )
				pass

			#button labels
			overlayDraw.text((3,27), "magn", fill=white)
			overlayDraw.text((3,58), "-", fill=white)
			overlayDraw.text((3,87), "menu", fill=white)

			#capture parameters
			metadata = picam2.capture_metadata()
			overlayDraw.text((103,20), " ag\n"+str(round(metadata["AnalogueGain"],1)), fill=white)
			overlayDraw.text((103,50), " dg\n"+str(round(metadata["DigitalGain"],1)), fill=white)
			overlayDraw.text((103,80), "  e\n1/"+str(int((metadata["ExposureTime"]/1000000)**(-1))), fill=white)

			#temperature of Raspi
			with open("/sys/class/thermal/thermal_zone0/temp") as f:
				temp = int(int(f.read().rstrip("\n"))/1000)
			overlayDraw.text((3, 114), f"t {str(temp)}", fill=white)

			#ip address
			connection = subprocess.check_output("hostname -I", shell=True, text=True)[:13]
			overlayDraw.text((28,114), f'|{connection if len(connection) >= 4 and connection[3] == "." else "no connection"}', fill=white)

			#magnification indicator
			if magnify_flag == True:
				overlayDraw.line((43,30,33,40), fill=0xffffff, width=3)
				overlayDraw.ellipse((38,25,48,35), fill=0xffffff)
				overlayDraw.ellipse((41,28,45,32), fill=0x000000)

			if energySavingFlag == True:
				overlayDraw.line((94,22,94,26), fill=0xffffff, width=2)
				overlayDraw.ellipse((91,9,97,23), fill=0xffffff)

			rotated_overlay = overlay.rotate(180)

		#get preview from camera
		preview_array = picam2.capture_array()
		preview = PIL.Image.fromarray(preview_array)
		#preview.paste(ImageOps.colorize(rotated_overlay, (0,0,0), (255,255,255)), (0,0), rotated_overlay) #white
		#preview.paste(ImageOps.colorize(rotated_overlay, (255,255,255), (0,0,0)), (0,0), rotated_overlay) #black
		#preview.paste(ImageOps.colorize(rotated_overlay, (0,0,0), (204,135,42)), (0,0), rotated_overlay) #orange
		preview.paste(ImageOps.colorize(rotated_overlay, (0,0,0), (172,117,50)), (0,0), rotated_overlay) #dark orange
		disp.LCD_ShowImage(preview, 0, 0)


def main():
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
	print(f"[-] LCD width:{LCD_1in44.LCD_WIDTH} height:{LCD_1in44.LCD_HEIGHT} scan dir:{Lcd_ScanDir}")

	# camera setup
	print("[!] setting up camera")
	picam2 = picamera2.Picamera2()
	capture_config = picam2.create_still_configuration()
	picam2.align_configuration(capture_config) #auto optimize config if applicable
	preview_config = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)}, transform=libcamera.Transform(hflip=1, vflip=1))
	picam2.align_configuration(preview_config)
	picam2.configure(preview_config)
	picam2.start()

	#print("Camera Controls:",picam2.camera_controls) #debug
	print(f"[#] DEBUG Capture Metadata:{picam2.capture_metadata()}") #['ScalerCrop'][2:]) #debug

	try:
		print("[!] starting run()")
		run(picam2, disp, preview_config, capture_config)
	except Exception as e:
		print(traceback.format_exc())

	print("[!] camera shutting down")
	picam2.stop()
	picam2.close()
	disp.LCD_Clear()
	RPi.GPIO.cleanup()
	print("[-] camera stopped")


if __name__ == "__main__":
	main()
