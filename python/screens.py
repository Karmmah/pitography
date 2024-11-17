#import PIL
from PIL import Image, ImageDraw
import LCD_1in44


black = 0x000000
grey = 0x999999
green = 0x00ff00


# startup screen
startup_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
startup_screen_draw = ImageDraw.Draw(startup_screen)
startup_screen_draw.rectangle( (50,50,LCD_1in44.LCD_WIDTH-50,LCD_1in44.LCD_HEIGHT-50), fill=green)

# main menu screen
mainMenuIndex = 1
main_menu_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
main_menu_screen_draw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0xffffff)
main_menu_screen_draw.polygon((59,58,69,58,64,53), fill=black) #up
main_menu_screen_draw.text((32,30), " Timelapse", fill=black)
main_menu_screen_draw.polygon((70,59,70,69,75,64), fill=black) #right
main_menu_screen_draw.text((80,58), " off", fill=black)
main_menu_screen_draw.polygon((59,70,69,70,64,75), fill=black) #down
main_menu_screen_draw.text((35,86), " Settings", fill=black)
main_menu_screen_draw.polygon((58,59,58,69,53,64), fill=black) #left
main_menu_screen_draw.text((10,58), " Photo", fill=black)
main_menu_screen = main_menu_screen.rotate(180)

# switch off screen
offScreenIndex = 2
offScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
offScreenDraw = ImageDraw.Draw(offScreen)
offScreenDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0x2222ff)
offScreenDraw.polygon((59,70,69,70,64,75), fill=black) #down
offScreenDraw.text((39,83), " Camera", fill=black)
offScreenDraw.text((37,92), " restart", fill=black)
offScreenDraw.polygon((59,58,69,58,64,53), fill=black) #up
offScreenDraw.text((40,30), " Pi off", fill=black)
offScreenDraw.polygon((58,59,58,69,53,64), fill=black) #left
offScreenDraw.text((14,58), " back", fill=black)
offScreen = offScreen.rotate(180)

# settings menu screen
settingsMenuIndex = 3
settings_menu_selected_item = 0
settingsMenuScreen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
settingsMenuDraw = ImageDraw.Draw(settingsMenuScreen)
settingsMenuDraw.rectangle((0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0xd89552)
settingsMenuDraw.text((25,8), " Settings")
settingsMenuDraw.text((4,30), " Exp. Mode")
settingsMenuDraw.text((4,47), " Shut. Lim.")

# capture success screen
capture_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
capture_screen_draw = ImageDraw.Draw(capture_screen)
capture_screen_draw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0 )
capture_screen_draw.text( (21,60), "Captured Image" )
capture_screen = capture_screen.rotate(180)
