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
#arrows
main_menu_screen_draw.polygon((59,58,69,58,64,53), fill=black) #up
main_menu_screen_draw.text((32,30), " Timelapse", fill=black)
main_menu_screen_draw.polygon((70,59,70,69,75,64), fill=black) #right
main_menu_screen_draw.text((75,58), " Pwr off", fill=black)
main_menu_screen_draw.polygon((59,70,69,70,64,75), fill=grey) #down
main_menu_screen_draw.text((32,86), " Settings", fill=grey)
main_menu_screen_draw.polygon((58,59,58,69,53,64), fill=black) #left
main_menu_screen_draw.text((11,58), " Photo", fill=black)
#labels
main_menu_screen = main_menu_screen.rotate(180)

# settings menu screen
settingsMenuIndex = 2
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
