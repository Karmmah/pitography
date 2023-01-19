#!/bin/sh

cd /home/pi/pi_camera

#echo "Testing the screen"
#python3 screentest.py

echo "Starting the Camera"
python3 simple_capture.py &

cd /home/pi/DCIM

echo "Starting the image http server"
sudo python3 -m http.server 80
