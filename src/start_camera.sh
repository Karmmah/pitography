#!/bin/sh

cd $HOME/pitography/src

echo "Starting the Camera"
#python3 simple_capture.py
#python3 pro_capture.py
#python3 camera64.py
python3 cameraDaemon.py
