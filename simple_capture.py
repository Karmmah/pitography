import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageOps
from io import BytesIO

import time, numpy
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

def main(ui, draw, cam):
	draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
	disp.LCD_ShowImage(ui, 0, 0)

#	(4056,3040) #max resolution, gpu_mem in /boot/config.txt needs to be changed to 256 to have enough resources for this resolution
	capture_resolution = (4056,3040)
	preview_resolution = (ui_width,ui_height)

	# fit preview to what will actually be captured at a given resolution
#	if capture_resolution[1] <= capture_resolution[0]: #landscape orientation
#		preview_zoom = ((1-capture_resolution[0]/4056)/2, (1-capture_resolution[1]/3040)/2, capture_resolution[1]/3040, capture_resolution[1]/3040)
#		preview_zoom = (0,0,1,1)
#	else: #portrait orientation
#		preview_zoom = ((1-3040/4056)/2+3040/4056*(capture_resolution[0]/3040)/2, 0, capture_resolution[0]/3040, capture_resolution[0]/3040)
#	print("preview_zoom", preview_zoom) #debug

	magnify_zoom = (0.35,0.35,0.3,0.3)

	cam.shutter_speed = 20000 #debug, set shutter speed to 1/50

	magnify_flag = False
	cam.resolution = preview_resolution
	cam.rotation = 180 #rotate for preview

	print("Running the program loop")
	while True:
		# capture image
		if GPIO.input(shutter_pin) == 0:
			# blank the backlight to visualise that the image is being taken
			GPIO.output(backlight_pin, 0)

			# set the capture resolution and reset crop
			cam.resolution = capture_resolution
			cam.rotation = 0
			magnify_flag = False
			cam.zoom = (0,0,1,1)

			# capture the image
			cam.capture( "/home/pi/DCIM/%d.jpg" % int(time.time()*1000) )
			print("image captured:", int(time.time()*1000))

			# display capture success message
			draw.rectangle( (0,0,ui_width,ui_height), fill=0 )
			draw.text( (0,0), "Image saved" )
#			draw.rotate(180)
			disp.LCD_ShowImage(ui, 0, 0)

			# reset resolution to preview
			cam.resolution = preview_resolution
			cam.rotation = 180

			# turn backlight back on
			GPIO.output(backlight_pin, 1)

		# show preview image on screen
		else:
#			cam.zoom = preview_zoom

			#preview variation 1 with Bytestream
#			stream = BytesIO()
#			cam.capture(stream, format="jpeg")
#			stream.seek(0)
#			preview = Image.open(stream)

			#preview variation 2 with numpy array
			data = numpy.empty( (preview_resolution[0],preview_resolution[1],3), dtype=numpy.uint8)
			cam.capture(data, "rgb")
			preview = Image.fromarray(data, "RGB")

			overlay = Image.new("L", (ui_width,ui_height))

			ov_draw = ImageDraw.Draw(overlay)

			if magnify_flag:
				#draw magnifying glass symbol to overlay
				ov_draw.ellipse( (100,10,110,20), fill=0xffffff )
				ov_draw.line( (105,15,95,25), fill=0xffffff, width=3 )

			# add current camera info to preview
			#properties of camera are saved as Fraction objects; need special handling
			gain = cam.analog_gain.numerator / cam.analog_gain.denominator

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
#camera.hflip = False
#camera.vflip = False
#camera.crop = (0.0, 0.0, 1.0, 1.0)

			ov_draw.text( (3,20), "gain "+str(round(gain,1)), fill=0xffffff )
			ov_draw.text( (3,30), "exp 1/"+str(int(1000000/cam.exposure_speed)), fill=0xffffff )
			ov_draw.text( (3,40), "shut 1/"+str(int(1000000/cam.shutter_speed)), fill=0xffffff )
			ov_draw.text( (3,50), "iso "+(str(cam.iso) if cam.iso != 0 else "auto"), fill=0xffffff )
#			ov_draw.text( (3,60), "bri "+str(cam.brightness), fill=0xffffff )
#			ov_draw.text( (3,70), "sha "+str(cam.sharpness), fill=0xffffff )

			overlay = overlay.rotate(180)
			preview.paste(ImageOps.colorize(overlay, (0,0,0), (255,255,255)), (0,0), overlay)

			disp.LCD_ShowImage(preview, 0, 0)

		# change magnification
		if GPIO.input(magnify_pin) == 0:
			magnify_flag = not magnify_flag

			if magnify_flag:
				cam.zoom = magnify_zoom
			else:
				cam.zoom = (0,0,1,1)

if __name__ == "__main__":
	try:
		draw.rectangle( (50,50,ui_width-50,ui_height-50), fill=0x00ff00)
		disp.LCD_ShowImage(ui, 0, 0)

		cam = pc.PiCamera(framerate=24)
#		time.sleep(2)
		cam.zoom = (0,0,1,1) #reset camera crop
		cam.start_preview() #preview to adjust exposure to available light

		main(ui, draw, cam)

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
