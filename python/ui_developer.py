#!/bin/python3

#from tkinter import Tk, Label
#from PIL import Image, ImageTk

import tkinter as tk
import PIL

import pitography_system


def check_input(key_nr):
    return key_nr


def main():

    # Create the main window
    root = tk.Tk()
    root.title("Image Display")

    # Open the image file
    #img = Image.open(image_path)


    i = 0
    while True:
        i = i+1 if i < 100 else 0

        input_key = check_input()
        if input_key != 0:
            ps.last_input_time = time.time()

        if time.time() - ps.last_input_time > 30:
            ps.energy_saving_flag = True
        else:
            ps.energy_saving_flag = False



    # Convert the image to a PhotoImage
    img_tk = PIL.ImageTk.PhotoImage(img)

    # Create a label widget to display the image
    label = Label(root, image=img_tk)
    label.pack()

    # Start the GUI event loop
    #root.mainloop()


if __name__ == "__main__":
    main()
