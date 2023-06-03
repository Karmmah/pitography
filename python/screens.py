#import PIL
from PIL import Image, ImageDraw
import LCD_1in44

# startup screen
startup_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
startup_screen_draw = ImageDraw.Draw(startup_screen)
startup_screen_draw.rectangle( (50,50,LCD_1in44.LCD_WIDTH-50,LCD_1in44.LCD_HEIGHT-50), fill=0x00ff00)

# main menu screen
main_menu_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
main_menu_screen_draw = ImageDraw.Draw(main_menu_screen)
main_menu_screen_draw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0xffffff)
#arrows
main_menu_screen_draw.polygon( (59,58,69,58,64,53), fill=0x000000) #up
main_menu_screen_draw.polygon( (70,59,70,69,75,64), fill=0x000000) #right
main_menu_screen_draw.polygon( (59,70,69,70,64,75), fill=0x000000) #down
main_menu_screen_draw.polygon( (58,59,58,69,53,64), fill=0x000000) #left
#labels
main_menu_screen_draw.text((32,30), " Timelapse", fill=0x000000)
main_menu_screen_draw.text((11,58), " Photo", fill=0x000000)
main_menu_screen_draw.text((75,58), " Pwr off", fill=0x000000)
main_menu_screen_draw.text((32,86), " Settings", fill=0x000000)
main_menu_screen = main_menu_screen.rotate(180)

# capture success screen
capture_screen = Image.new("RGB", (LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT))
capture_screen_draw = ImageDraw.Draw(capture_screen)
capture_screen_draw.rectangle( (0,0,LCD_1in44.LCD_WIDTH,LCD_1in44.LCD_HEIGHT), fill=0 )
capture_screen_draw.text( (17,60), "Capturing Image" )
capture_screen = capture_screen.rotate(180)
