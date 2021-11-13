import tkinter
from picamera import PiCamera
import time
from gpiozero import Button

up = Button(26)
down = Button(5)
left = Button(6)
right = Button(19)
press = Button(13)
key1 = Button(21)
key2 = Button(20)
key3 = Button(16)

pwidth = 300 #width of the program window
pheight = 260
#max resolution: 4056x3040
rwidth = 2028 #resolution width
rheight = 1520

camera = PiCamera()
#camera.resolution = (rwidth,rheight) #reset resolution at start
camera.crop = (0,0,1,1) #reset crop at start

def write_error(_input_):
    file = open('camera_errors.txt','w')
    file.write(str(int(time.time()))+' '+_input_+'\n')
    file.close()

def capture():
    #camera.resolution = (rwidth,rheight)
    camera.crop = (0,0,1,1)
    camera.stop_preview()
    camera.capture('/home/pi/Pictures/picamera/%s.jpg' %str(int(time.time())))

#def get_gain(): #get analog gain in decimal number instead of fraction
#    gain = camera.analog_gain
#    if len(input) == 1:
#        pass
#    else:
#        content = list(map(int,input.split('/')))
#        gain = round(content[0]/content[1],2)
#    return gain

def __info__():
    l_iso['text'] = 'iso:\n'+str(camera.iso)
    l_expo['text'] = 'exposure:\n'+str(camera.exposure_speed)
    #try:
    #    l_gain['text'] = 'gain:\n'+str(get_gain())
    #except Exception as e:
    #    l_error = tkinter.Label(root, text=e, font=('Arial',12))
    #    l_error.place(relx=0,rely=0)
    #l_bright['text'] = 'brightness:\n'+str(camera.brightness)

global preview
preview = False
def preview():
    global preview
    if preview:
        camera.stop_preview()
    else:
        camera.start_preview(fullscreen=True) #False, window=(0,0,300,300))
    preview = not preview #switch the preview

global mag
mag = False
def magnification():
    global mag
    if mag:
        camera.crop = (0,0,1,1)
    else:
        #x_factor = 4056/rwidth
        #y_factor = 3040/rheight
        camera.crop = (0.4,0.4,0.2,0.2)
    mag = not mag #switch the magnifiaciton


key3.when_pressed = preview
key2.when_pressed = __info__
key1.when_pressed = magnification
press.when_pressed = capture


root = tkinter.Tk()
root.title('simple capture')
root.geometry('%sx%s' %(pwidth, pheight))
root.configure(bg='white')

font1 = ('Eras Bold ITC', 24)

l_iso = tkinter.Label(root, text='ISO', font=font1)
l_iso.place(anchor='nw', relx=0, rely=0)
l_iso_value = tkinter.Label(root, text=str(camera.iso), font=font1)
l_iso_value.place(anchor='ne', relx=1, rely=0)
try:
    l_expo = tkinter.Label(root, text='EXPOSURE', font=font1)
    l_expo.place(anchor='w', relx=1, rely=0.3)
    l_expo_value = tkinter.Label(root, text=str(camera.exposure), font=font1)
    l_expo_value.place(anchor='e', relx=1, rely=0.3)
except Exception as e:
    write_error(e)
#l_gain = tkinter.Label(root, text='gain:\n'+str(camera.analog_gain), font=font1)
#l_gain.place(anchor='sw',relx=0,rely=1)
#l_bright = tkinter.Label(root, text='brightness:\n'+str(camera.brightness), font=font1)
#l_bright.place(anchor='se',relx=1,rely=1)

try:
    root.mainloop()
finally:
    #camera.stop_preview()
    camera.close()
