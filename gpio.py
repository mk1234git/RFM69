#!/usr/bin/python

import RPi.GPIO as GPIO

print GPIO.RPI_INFO

GPIO.setmode(GPIO.BOARD)

pin = 1
for pin in range(28):
    try:
        print "pin:", pin
        func = GPIO.gpio_function(pin)
        print func
    except:
        pass
