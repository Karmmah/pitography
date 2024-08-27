# module containing system code for pitography

import PIL, time

# colors
black = 0x000000
white = 0xffffff
grey  = 0x999999
red   = 0x0000ff
green = 0x00ff00


# menu
main_menu_index = 1
current_menu_index = 0

main_menu_screen_draw = PIL.ImageDraw.Draw(screens.main_menu_screen)

overlay = PIL.Image.new("L", (LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))
overlay_draw = PIL.ImageDraw.Draw(overlay)
rotated_overlay = overlay.rotate(180)


# capture modes
still_capture_index = 0
timelapse_capture_index = 1

current_capture_mode = still_capture_index #default value


# magnify preview
magnify_flag = False


# timelapse
timelapse_capture_flag = False
last_timelapse_frame_time = 0
last_timelapse_exposure_times = [] #save exposure times of the last photos taken to smooth out exposure
timelapse_start_str = "no_timelapse_started"
timelapse_frame_nr = 0

timelapse_interval = 5 #temporary, change when timelapse menu is implemented


# energy saving mode
last_input_time = time.time()
energy_saving_flag = False


def check_energy_saver_activation():
    if time.time() - ps.last_input_time > 30:
        energy_saving_flag = True
    else:
        energy_saving_flag = False
