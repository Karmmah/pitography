import tkinter, time

#parameters
pwidth = 300 #width of the program window
pheight = 260

def capture():
	#camera.resolution = (rwidth,rheight)
	camera.crop = (0,0,1,1)
	camera.stop_preview()
	camera.capture('/home/pi/Pictures/picamera/%s.jpg' % str(int(time.time())))

global preview, magnification
preview, magnification = False, False

def preview():
	global preview
	if preview:
		camera.stop_preview()
	else:
		camera.start_preview(fullscreen=True) #False, window=(0,0,300,300))
	preview = not preview #switch the preview

def change_magnification():
	global magnification
	if magnification:
		camera.crop = (0,0,1,1)
	else:
		camera.crop = (0.4,0.4,0.2,0.2)
	magnification = not magnification #switch the magnification

def main():
#	with open("/home/pi/Desktop/launch.txt", "a") as f:
#		f.write(str(int(time.time())))
	root = tkinter.Tk()
	root.title('simple capture')
	root.geometry('%sx%s' %(pwidth, pheight))
	root.configure(bg='white')
	font1 = ('Eras Bold ITC', 24)

	l_test = tkinter.Label(root, text="Test", font=font1)

	l_test.pack()

	from picamera import PiCamera
	from gpiozero import Button
	try:

		down = Button(5)
		up = Button(26)
		left = Button(6)
		right = Button(19)
		center = Button(13)
		key1 = Button(21)
		key2 = Button(20)
		key3 = Button(16)

		key3.when_pressed = preview
		key1.when_pressed = change_magnification
		center.when_pressed = capture

		camera = PiCamera()
		camera.crop = (0,0,1,1) #reset crop at start
#		camera.resolution = (rwidth,rheight) #reset resolution at start

	except Exception as e:
		with open("/home/pi/Desktop/errors.txt", "a") as f:
			f.write("error")
			f.write(e)
		l_test['text'] = "error" #str(e)

	try:
		root.mainloop()
	finally:
		#camera.stop_preview()
		pass
#		camera.close()

if __name__ == "__main__":
	main()

#l_iso = tkinter.Label(root, text='ISO', font=font1)
#l_iso.place(anchor='nw', relx=0, rely=0)
#l_iso_value = tkinter.Label(root, text=str(camera.iso), font=font1)
#l_iso_value.place(anchor='ne', relx=1, rely=0)
#try:
#    l_expo = tkinter.Label(root, text='EXPOSURE', font=font1)
#    l_expo.place(anchor='w', relx=1, rely=0.3)
#    l_expo_value = tkinter.Label(root, text=str(camera.exposure), font=font1)
#    l_expo_value.place(anchor='e', relx=1, rely=0.3)

########################



#max resolution: 4056x3040
rwidth = 4056 #2028 #resolution width
rheight = 3040 #1520

#def get_gain(): #get analog gain in decimal number instead of fraction
#    gain = camera.analog_gain
#    if len(input) == 1:
#        pass
#    else:
#        content = list(map(int,input.split('/')))
#        gain = round(content[0]/content[1],2)
#    return gain

#def __info__():
#    l_iso['text'] = 'iso:\n'+str(camera.iso)
#    l_expo['text'] = 'exposure:\n'+str(camera.exposure_speed)
#    #try:
#    #    l_gain['text'] = 'gain:\n'+str(get_gain())
#    #except Exception as e:
#    #    l_error = tkinter.Label(root, text=e, font=('Arial',12))
#    #    l_error.place(relx=0,rely=0)
#    #l_bright['text'] = 'brightness:\n'+str(camera.brightness)





#l_gain = tkinter.Label(root, text='gain:\n'+str(camera.analog_gain), font=font1)
#l_gain.place(anchor='sw',relx=0,rely=1)
#l_bright = tkinter.Label(root, text='brightness:\n'+str(camera.brightness), font=font1)
#l_bright.place(anchor='se',relx=1,rely=1)


