#!/bin/python3

import picamera2, libcamera
import PIL
from PIL import ImageOps
import io
import traceback
import time
import subprocess

from src import LCD_Config, LCD_1in44
import RPi.GPIO
from src import screens


#available keys on waveshare 1.44in LCD HAT
#PIN        Pi Interface (BCM)  Description
#KEY1               P21          KEY1GPIO
#KEY2               P20          KEY2GPIO
#KEY3               P16          KEY3GPIO
#Joystick UP        P6           Upward direction of the Joystick
#Joystick Down      P19          Downward direction of the Joystick
#Joystick Left      P5           Left direction of the Joystick
#Joystick Right     P26          Right direction of the Joystick
#Joystick Press     P13          Press the Joystick
#SCLK               P11/SCLK     SPI clock line
#MOSI               P10/MOS      SPI data line
#CS                 P8/CE0       Chip selection
#DC                 P25          Data/Command control
#RST                P27          Reset
#BL                 P24          Backlight

# button mapping (mirrored to references given above)
KEY1_PIN      = 21
KEY2_PIN      = 20
KEY3_PIN      = 16
UP_PIN        = 19
DOWN_PIN      = 6
LEFT_PIN      = 26
RIGHT_PIN     = 5
PRESS_PIN     = 13
BACKLIGHT_PIN = 24

RED   = 0x0000ff
WHITE = 0xffffff
BLACK = 0x000000


def check_input():
    if RPi.GPIO.input(KEY1_PIN) == 0:
        return 21
    elif RPi.GPIO.input(KEY2_PIN) == 0:
        return 20
    elif RPi.GPIO.input(KEY3_PIN) == 0:
        return 16
    elif RPi.GPIO.input(UP_PIN) == 0:
        return 19
    elif RPi.GPIO.input(DOWN_PIN) == 0:
        return 6
    elif RPi.GPIO.input(LEFT_PIN) == 0:
        return 26
    elif RPi.GPIO.input(RIGHT_PIN) == 0:
        return 5
    elif RPi.GPIO.input(PRESS_PIN) == 0:
        return 13
    else:
        return 0


def run(picam2, disp, previewConfig, captureConfig):
    currentMenuIndex = 0
    settingsMenuSelectedItem = 0

    stillCaptureIndex = 0
    timelapseCaptureIndex = 1
    timelapseCaptureFlag = False
    lastTimelapseFrameTime = 0
    lastTimelapseExposureTimes = [] #save exposure times of the last photos taken to smooth out exposure
    timelapseStartStr = "no_timelapse_started"
    timelapseFrameNr = 0

    timelapseInterval = 5 #temporary, change when timelapse menu is implemented

    exposureModes = ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks']
    exposureModeIndex = 6 #default: sports

    currentCaptureMode = stillCaptureIndex #default value

    buttonHoldFlag = False
    magnifyFlag = False

    lastInputTime = time.time()
    energySavingFlag = False

    mainMenuScreenDraw = PIL.ImageDraw.Draw(screens.mainMenuScreen)

    overlay = PIL.Image.new("L", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
    overlayDraw = PIL.ImageDraw.Draw(overlay)
    rotated_overlay = overlay.rotate(180)

    counter = 0 #for doing stuff only every nth update cycle
    while True: #program loop
        counter = counter+1 if counter < 100 else 0

        inputKey = check_input()
        if inputKey != 0:
            lastInputTime = time.time()
            energySavingFlag = False

        if time.time() - lastInputTime > 30: #enable energy saver after 30 s of no input
            energySavingFlag = True
#        else:
#            energySavingFlag = False

        # check if button is held
        if buttonHoldFlag == True:
            if inputKey == 0:
                buttonHoldFlag = False
            else:
                inputKey = 0
        elif inputKey != 0:
            lastInputTime = time.time()
            buttonHoldFlag = True
#        print("[!] DEBUG input key:{inputKey} button hold:{buttonHoldFlag}")

        # show menu
        if currentMenuIndex == 0 and inputKey == KEY1_PIN:
            currentMenuIndex = screens.mainMenuIndex
            continue

        #main menu
        elif currentMenuIndex == screens.mainMenuIndex:
            # draw active capture mode indicator
            mainMenuScreenDraw.line((106,56,88,56), width=2, fill=RED if currentCaptureMode == stillCaptureIndex else WHITE)
            mainMenuScreenDraw.line((46,83,82,83), width=2, fill=RED if currentCaptureMode == timelapseCaptureIndex else WHITE)
            disp.LCD_ShowImage(screens.mainMenuScreen, 0, 0)
            #inputKey = 0

            while inputKey == 0:
                inputKey = check_input()
                time.sleep(0.1)

            if inputKey in [PRESS_PIN, KEY2_PIN, KEY3_PIN]:
                currentMenuIndex = 0
                time.sleep(0.2)
                continue
            elif inputKey == DOWN_PIN:
                currentMenuIndex = screens.settingsMenuIndex
                continue
            elif inputKey == LEFT_PIN:
                currentCaptureMode = stillCaptureIndex
                currentMenuIndex = 0
                continue
            elif inputKey == UP_PIN:
                currentCaptureMode = timelapseCaptureIndex
                currentMenuIndex = 0
                continue
            elif inputKey == RIGHT_PIN:
                currentMenuIndex = screens.offScreenIndex
            else:
                time.sleep(0.2)
                continue

        #off menu
        elif currentMenuIndex == screens.offScreenIndex:
            disp.LCD_ShowImage(screens.offScreen, 0, 0)
            #inputKey = 0
            while inputKey == 0:
                inputKey = check_input()
                time.sleep(0.1)
            if inputKey == LEFT_PIN:
                currentMenuIndex = screens.mainMenuIndex
            elif inputKey == DOWN_PIN:
                print("[!] shutdown")
                subprocess.run("sudo shutdown now", shell=True, text=True)
                print("[-------shutdown-------]")
                return
            elif inputKey == UP_PIN:
                print("[!] exit camera")
                return
            else:
                time.sleep(0.2)
                continue

        #settings menu
        elif currentMenuIndex == screens.settingsMenuIndex:
            inputKey = 0
            while inputKey == 0: #TODO change loop so that settings menu part is not exited before settings menu is exited
                inputKey = check_input()
                time.sleep(0.1)

            if inputKey == PRESS_PIN: #exit menu
                currentMenuIndex = 0
            elif inputKey == KEY1_PIN: #return to menu
                currentMenuIndex = 1
            elif inputKey == DOWN_PIN:
                settingsMenuSelectedItem += 1 if settingsMenuSelectedItem < 1 else 0
            elif inputKey == UP_PIN:
                settingsMenuSelectedItem -= 1 if settingsMenuSelectedItem > 0 else 0
            elif inputKey == LEFT_PIN and settingsMenuSelectedItem == 0:
                exposureModeIndex -= 1 if exposureModeIndex > 0 else 0
                picam2.exposure_mode = exposureModes[exposureModeIndex]
            elif inputKey == RIGHT_PIN and settingsMenuSelectedItem == 0:
                exposureModeIndex += 1 if exposureModeIndex < len(exposureModes)-1 else 0
                picam2.exposure_mode = exposureModes[exposureModeIndex]
            elif inputKey == LEFT_PIN and settingsMenuSelectedItem == 1:
                shutterLimitFlag = False
            elif inputKey == RIGHT_PIN and settingsMenuSelectedItem == 1:
                shutterLimitFlag = True

            # update menu screen
            screens.settingsMenuDraw.rectangle((70,31,128,40), fill=0xd89552) #erase old value
            screens.settingsMenuDraw.text((70,30), text=exposureModes[exposureModeIndex], fill=0x00c7ff if settingsMenuSelectedItem == 0 else 0xffffff)
            screens.settingsMenuDraw.rectangle((70,48,105,56), fill=0xd89552) #erase old value
            #screens.settingsMenuDraw.text((70,47), text=" %s" % (shutterLimitFlag), fill=0x00c7ff if settingsMenuSelectedItem == 1 else 0xffffff)
            screens.settingsMenuDraw.text((70,47), text="shutter limit", fill=0x00c7ff if settingsMenuSelectedItem == 1 else 0xffffff)

            settingsMenuScreen = screens.settingsMenuScreen.rotate(180)
            disp.LCD_ShowImage(settingsMenuScreen, 0, 0)
            continue

        # change magnification
        if inputKey == KEY3_PIN:
            magnifyFlag = not magnifyFlag
            if magnifyFlag == True:
                picam2.set_controls({"ScalerCrop": (1572,1064,912,912)})
            else:
                picam2.set_controls({"ScalerCrop": (508,0,3040,3040)})

        # capture still image
        if currentCaptureMode == stillCaptureIndex and inputKey == PRESS_PIN:
            print("[!] capture start")
            #RPi.GPIO.output(BACKLIGHT_PIN, 0)
            magnifyFlag = False
            imageName = time.strftime("%Y%m%d_%H%M%S")+".jpg"
            #picam2.switch_mode_and_capture_file(captureConfig, f"/home/pi/DCIM/{imageName}")
            picam2.stop()
            picam2.configure(captureConfig)
            error = 1
            while error != 0:
                try:
                    picam2.start()
                    picam2.capture_file(f'/home/pi/DCIM/{imageName}', format="jpeg")
                    error = 0
                except Exception as err:
                    print(f"\t[!] error #{error}:{err}\n\tretrying")
                    picam2.stop()
                    error += 1
            picam2.stop()
            picam2.configure(previewConfig)
            picam2.start()
            print(f"[!] captured {imageName}")
            disp.LCD_ShowImage(screens.captureScreen, 0, 0)
            #RPi.GPIO.output(BACKLIGHT_PIN, 1)
            lastInputTime = time.time() #avoid energy saving from inactivity during capture

        # capture timelapse
        #switch timelapse capture on/off
        if currentCaptureMode == timelapseCaptureIndex and inputKey == PRESS_PIN: #start or stop timelapse capture
            timelapseCaptureFlag = not timelapseCaptureFlag
            if timelapseCaptureFlag == True:
                timelapseStartStr = time.strftime("%Y%m%d_%H%M%S")
                timelapseFrameNr = 1
            print(f"[#] DEBUG timelapse capture: timelapseCaptureFlag:{timelapseCaptureFlag}")

        if timelapseCaptureFlag:
            if time.time() > (lastTimelapseFrameTime + timelapseInterval):
                RPi.GPIO.output(BACKLIGHT_PIN, 0)
                #if len(lastTimelapseExposureTimes) < 10:
                #    lastTimelapseExposureTimes += [picam2.exposure_speed]
                #else:
                #    lastTimelapseExposureTimes = lastTimelapseExposureTimes[0:9]+[picam2.exposure_speed]
                #    avg_exposure = int(round((lastTimelapseExposureTimes[0]+lastTimelapseExposureTimes[1]+lastTimelapseExposureTimes[2]+lastTimelapseExposureTimes[3]+lastTimelapseExposureTimes[4]+lastTimelapseExposureTimes[5]+lastTimelapseExposureTimes[6]+lastTimelapseExposureTimes[7]+lastTimelapseExposureTimes[8]+lastTimelapseExposureTimes[9])/10, 0))
                #    picam2.shutter_speed = avg_exposure
                #    picam2.set_controls({"ExposureTime": avg_exposure})
                timelapseFrameNrStr = "%04d" % timelapseFrameNr
                imageName = f"{timelapseStartStr}_{timelapseFrameNrStr}.jpg"
                picam2.stop()
                picam2.configure(captureConfig)
                picam2.start()
                picam2.capture_file(f'/home/pi/DCIM/timelapse/{imageName}')
                timelapseFrameNr += 1
                lastTimelapseFrameTime = time.time()
                picam2.stop()
                picam2.configure(previewConfig)
                picam2.start()
                print(f"[!] captured {imageName}")
                RPi.GPIO.output(BACKLIGHT_PIN, 1)

        # show preview
        if energySavingFlag == True and counter % 7 != 0: #reduce screen refresh rate in energy save mode
            time.sleep(0.1)
            continue #move back to top of while loop and skip rendering overlay

        #populate overlay
        if counter % 5 == 0: #update preview every nth cycle
            overlayDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=BLACK)

            #capture mode
            if currentCaptureMode == timelapseCaptureIndex:
                overlayDraw.text( (1,1), " Timelapse", fill=WHITE ) #drop shadow to make it look nicer
                overlayDraw.text( (0,0), " Timelapse", fill=WHITE )
                overlayDraw.text( (72,0), f"{timelapseInterval}s", fill=WHITE)
                if timelapseCaptureFlag:
                    overlayDraw.text( (36,14), "capturing", fill=WHITE )
                    #time.sleep(0.2) #reduce preview rate to reduce power consumption during timelapse recording
            elif currentCaptureMode == stillCaptureIndex:
                #overlayDraw.text( (1,1), " Photo", fill=WHITE ) #drop shadow like to make it look nicer
                #overlayDraw.text( (0,0), " Photo", fill=WHITE )
                pass #show no text for default mode

            #button labels
            overlayDraw.text( (3,27), "magn", fill=WHITE )
            overlayDraw.text( (3,58), "-", fill=WHITE )
            overlayDraw.text( (3,87), "menu", fill=WHITE )

            #capture parameters
            metadata = picam2.capture_metadata()
            overlayDraw.text( (90,20), " ag".rjust(6)+'\n'+(str(round(metadata["AnalogueGain"],1))).rjust(6), fill=WHITE )
            overlayDraw.text( (90,50), " dg".rjust(6)+'\n'+(str(round(metadata["DigitalGain"],1))).rjust(6), fill=WHITE )
            overlayDraw.text( (90,80), " e".rjust(6)+'\n'+("1/"+str(int((metadata["ExposureTime"]/1000000)**(-1)))).rjust(6), fill=WHITE )

            #temperature of Raspi
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp = int(int(f.read().rstrip("\n"))/1000)
            overlayDraw.text( (103, 3), f"t {str(temp)}", fill=WHITE )

            #ip address
            connection = subprocess.check_output("hostname -I", shell=True, text=True)[:13]
            overlayDraw.text( (3,114), f'{connection if len(connection) >= 4 and connection[3] == "." else "no connection"}', fill=WHITE )

            #magnification indicator
            if magnifyFlag == True:
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
#    RPi.GPIO.setwarnings(False)
    RPi.GPIO.setup(KEY3_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(KEY2_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(KEY1_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(UP_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(DOWN_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(LEFT_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(RIGHT_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(PRESS_PIN, RPi.GPIO.IN, pull_up_down = RPi.GPIO.PUD_UP)
    RPi.GPIO.setup(BACKLIGHT_PIN, RPi.GPIO.OUT, initial=1)

    # display setup
    print("[!] setting up display")
    disp = LCD_1in44.LCD()
    lcdScanDir = LCD_1in44.SCAN_DIR_DFT
    disp.LCD_Init(lcdScanDir)
    #disp.LCD_Clear()
    disp.LCD_ShowImage(screens.startupScreen, 0, 0)
    print(f"[-] LCD width:{LCD_1in44.LCD_WIDTH} height:{LCD_1in44.LCD_HEIGHT} scan dir:{lcdScanDir}")

    # camera setup
    print("[!] setting up camera")
    picam2 = picamera2.Picamera2()
    captureConfig = picam2.create_still_configuration()
    picam2.align_configuration(captureConfig) #auto optimize config if applicable
    previewConfig = picam2.create_preview_configuration(main={"size":(LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT)}, transform=libcamera.Transform(hflip=1, vflip=1))
    picam2.align_configuration(previewConfig)
    picam2.configure(previewConfig)
    picam2.start()

    print(f"[#] DEBUG Camera Properties: {picam2.camera_properties}")
    print(f"[#] DEBUG Camera Controls: {picam2.camera_controls}")
    print(f"[#] DEBUG Capture Metadata: {picam2.capture_metadata()}")

    try:
        print("[!] running camera")
        run(picam2, disp, previewConfig, captureConfig)
    except Exception as e:
        print(traceback.format_exc())

    print("[!] camera shutting down")
    picam2.stop()
    picam2.close()
    disp.LCD_Clear()
    RPi.GPIO.cleanup()
    print("[!] camera stopped")


if __name__ == "__main__":
    main()
