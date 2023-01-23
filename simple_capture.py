import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
from io import BytesIO

import time, numpy, subprocess
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

# ui parameters
ui_width, ui_height = 128, 128
#(4056,3040) #max resolution, gpu_mem in /boot/config.txt needs to be changed to 256 to have enough resources for this resolution
#capture_resolution = (4056,3040)
capture_resolution = (4032,3040)
preview_resolution = (ui_width,ui_height)

# create startup image
startup_image = Image.new("RGB", (ui_width,ui_height))
startup_image_draw = ImageDraw.Draw(startup_image)
startup_image_draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)

# create capture success screen
capture_success = Image.new("RGB", (ui_width,ui_height))
capture_success_draw = ImageDraw.Draw(capture_success)
capture_success_draw.rectangle( (0,0,ui_width,ui_height), fill=0 )
capture_success_draw.text( (0,0), "Image saved" )
capture_success = capture_success.rotate(180)

# GPIO init
GPIO.setmode(GPIO.BCM)
GPIO.setup(shutter_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(backlight_pin, GPIO.OUT, initial=1)
GPIO.setup(magnify_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def main(cam):
	magnify_zoom = (0.35,0.35,0.3,0.3)

	min_shutter_speed = 20000 #minimal shutter speed 1/50 (20000 µs)

	magnify_flag = False
	cam.resolution = preview_resolution
	cam.rotation = 180 #rotate for preview

	print("Running the program loop")
	while True:
		#check if current needed exposure speed calculated by the camera is lower than the minimum
		if cam.exposure_speed > min_shutter_speed:
#			print("too dark", cam.exposure_speed)
			cam.shutter_speed = min_shutter_speed

		# capture image
		if GPIO.input(shutter_pin) == 0:
			# blank the backlight to visualise that the image is being taken
			GPIO.output(backlight_pin, 0)

			# set the capture resolution and reset crop, rotation and magnification
			cam.resolution = capture_resolution
			cam.rotation = 0
			magnify_flag = False
			cam.zoom = (0,0,1,1)

			# capture the image
#			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000), format="raw" )
#			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000), format=".jpg", bayer=True )
			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000) )
			print("image captured:", int(time.time()*1000))

			# display capture success message
			disp.LCD_ShowImage(capture_success, 0, 0)

			# reset resolution to preview
			cam.resolution = preview_resolution
			cam.rotation = 180

			# turn backlight back on
			GPIO.output(backlight_pin, 1)

		# show preview image on screen
		#preview variation 1 with Bytestream
#		stream = BytesIO()
#		cam.capture(stream, format="jpeg")
#		stream.seek(0)
#		preview = Image.open(stream)

		#preview variation 2 with numpy array
		data = numpy.empty( (preview_resolution[0],preview_resolution[1],3), dtype=numpy.uint8)
		cam.capture(data, "rgb")
		preview = Image.fromarray(data, "RGB")

		overlay = Image.new("L", (ui_width,ui_height))

		ov_draw = ImageDraw.Draw(overlay)

		#draw magnifying glass symbol to overlay
		if magnify_flag:
			ov_draw.ellipse( (98,20,108,30), fill=0xffffff )
			ov_draw.line( (103,25,93,35), fill=0xffffff, width=3 )

#		if subprocess.check_output("systemctl is-active file_server", text=True, shell=True) == "active\n":
#			ov_draw.text( (30,100), text="fs running", fill=0x00ff00 )
#		else:
#			ov_draw.text( (30,100), text="fs not running", fill=0xff0000 )

		# check if internet connection is available and displey the cameras ip address
		ov_draw.text( (25,115), text=subprocess.check_output("hostname -I", text=True, shell=True)[:13], fill=0xffffff)

#from the pi camera guide
#camera.brightness = 50 (0 to 100)
#camera.sharpness = 0 (-100 to 100)
#camera.contrast = 0 (-100 to 100)
#camera.saturation = 0 (-100 to 100)
#camera.iso = 0 (automatic) (100 to 800)
#camera.exposure_compensation = 0 (-25 to 25)
#camera.exposure_mode = 'auto'
#camera.meter_mode = 'average'
#camera.awb_mode = 'auto'
#camera.rotation = 0
#camera.crop = (0.0, 0.0, 1.0, 1.0)

		# add current camera info to preview
		#properties of camera are saved as Fraction objects; need special handling
		ag = cam.analog_gain.numerator / cam.analog_gain.denominator
		dg = cam.digital_gain.numerator / cam.digital_gain.denominator
		ov_draw.text( (3,10), "ag "+str(round(ag,1)), fill=0xffffff )
		ov_draw.text( (3,20), "dg "+str(round(dg,1)), fill=0xffffff )
		ov_draw.text( (3,30), "e 1/"+str(int(1000000/cam.exposure_speed)), fill=0xffffff )
		ov_draw.text( (3,40), "s 1/"+(str(int(1000000/cam.shutter_speed)) if cam.shutter_speed > 0 else "0"), fill=0xffffff )
		ov_draw.text( (3,50), "i "+(str(cam.iso) if cam.iso != 0 else "auto"), fill=0xffffff )
#		ov_draw.text( (3,60), "comp "+str(cam.exposure_compensation), fill=0xffffff )

		overlay = overlay.rotate(180)
		preview.paste(ImageOps.colorize(overlay, (0,0,0), (255,255,255)), (0,0), overlay)

		disp.LCD_ShowImage(preview, 0, 0)

if __name__ == "__main__":
	try:
		disp.LCD_ShowImage(startup_image, 0, 0)

		cam = pc.PiCamera(framerate=24)
#		time.sleep(2)
		cam.zoom = (0,0,1,1) #reset camera crop
		cam.start_preview() #preview to let the camera adjust exposure to available light

		main(cam)

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
