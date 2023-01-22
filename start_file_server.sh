#!/bin/sh

cd /home/pi/DCIM

echo "Starting the image http server"
sudo python3 -m http.server 80
