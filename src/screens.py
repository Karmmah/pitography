#import PIL
from PIL import Image, ImageDraw
from src import LCD_1in44


BLACK = 0x000000
GREY = 0x999999
GREEN = 0x00ff00


# STARTUP SCREEN
startupScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
startupScreenDraw = ImageDraw.Draw(startupScreen)
startupScreenDraw.rectangle( (50,50,LCD_1in44.LCD_WIDTH-50,LCD_1in44.LCD_HEIGHT-50), fill=GREEN)

# CAPTURE SUCCESS SCREEN
captureScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
captureScreenDraw = ImageDraw.Draw(captureScreen)
captureScreenDraw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0 )
captureScreenDraw.text( (21,60), "Captured Image" )
captureScreen = captureScreen.rotate(180)

# MAIN MENU SCREEN
mainMenuIndex = 1
mainMenuScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
mainMenuScreenDraw = ImageDraw.Draw(mainMenuScreen)
mainMenuScreenDraw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0xffffff)
mainMenuScreenDraw.polygon((59,58,69,58,64,53), fill=BLACK) #up
mainMenuScreenDraw.text((32,30), " Timelapse", fill=BLACK)
mainMenuScreenDraw.polygon((70,59,70,69,75,64), fill=BLACK) #right
mainMenuScreenDraw.text((80,58), " off", fill=BLACK)
mainMenuScreenDraw.polygon((59,70,69,70,64,75), fill=BLACK) #down
mainMenuScreenDraw.text((35,86), " Settings", fill=BLACK)
mainMenuScreenDraw.polygon((58,59,58,69,53,64), fill=BLACK) #left
mainMenuScreenDraw.text((10,58), " Photo", fill=BLACK)
mainMenuScreen = mainMenuScreen.rotate(180)

# SWITCH OFF SCREEN
offScreenIndex = 2
offScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
offScreenDraw = ImageDraw.Draw(offScreen)
offScreenDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0x2222ff)
offScreenDraw.polygon((59,70,69,70,64,75), fill=BLACK) #down
offScreenDraw.text((40,83), " Pi off", fill=BLACK)
offScreenDraw.polygon((59,58,69,58,64,53), fill=BLACK) #up
offScreenDraw.text((39,26), " Camera", fill=BLACK)
offScreenDraw.text((37,35), " restart", fill=BLACK)
offScreenDraw.polygon((58,59,58,69,53,64), fill=BLACK) #left
offScreenDraw.text((14,58), " back", fill=BLACK)
offScreen = offScreen.rotate(180)

# SETTINGS MENU SCREEN
settingsMenuIndex = 3
settingsMenuSelectedItem = 0
settingsMenuScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
settingsMenuDraw = ImageDraw.Draw(settingsMenuScreen)
settingsMenuDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0xd89552)
settingsMenuDraw.text((32,8), " Settings")
settingsMenuDraw.text((4,30), " ExpoMode")
settingsMenuDraw.text((4,47), " ShutrLim")

# TIMELAPSE MENU SCREEN
timelapseMenuIndex = 4
timelapseMenuScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
timelapseMenuDraw = ImageDraw.Draw(timelapseMenuScreen)
timelapseMenuDraw.text((31,8), " Timelapse")
