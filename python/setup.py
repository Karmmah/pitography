#!/bin/python3

from setuptools import setup, find_packages


with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name = "pitography"
    author = "Karmmah"
    description = "photography camera with RaspberryPi and HQ camera module"
    long_description = long_description
    install_requires = [
        "picamera2",
    ]
    entry_points = {
        "console_scripts":[
        ],
    },
)
