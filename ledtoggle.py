#!/usr/bin/env python

"""This runs on raspberry pi and allows the toggling of an LED.

All you need is a 220-330 ohm resistor on the anode side of the LED.
This was run off pin 18.
"""

import time
import RPi.GPIO as GPIO

class Toggler(object):
    def __init__(self):
        """True is ON and False is OFF."""
        self.gpio = GPIO
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)
        self.gpio.setup(18,self.gpio.OUT)
        self.state = False
        
    def toggle(self): 
        if self.state:
            print "LED on"
            self.gpio.output(18,self.gpio.HIGH)  
        else:
            print "LED off"
            self.gpio.output(18,self.gpio.LOW)
        self.state = not self.state

state = Toggler()
try:
    while True:
        command = raw_input('Hit enter to toggle!')
        if command == '':
            state.toggle()
except KeyboardInterrupt:
    print "exiting..."
    state.gpio.cleanup()

