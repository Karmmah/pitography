#!/bin/python3

import RPi.GPIO
import camera64
from importlib import reload


def main():
	while True:
		camera64.main()
		print("[!] restarting camera")
		reload(camera64)
		reload(camera64.screens)


if __name__ == "__main__":
	main()
