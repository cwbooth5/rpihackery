#!/usr/bin/env python

"""
This is only really useful for demonstrating the reading of a trimpot value
through an ADC.

https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/connecting-the-cobbler-to-a-mcp3008?view=all
MCP3008 VDD -> 3.3V (red)
MCP3008 VREF -> 3.3V (red)
MCP3008 AGND -> GND (black)
MCP3008 CLK -> #18 (orange)
MCP3008 DOUT -> #23 (yellow)
MCP3008 DIN -> #24 (blue)
MCP3008 CS -> #25 (violet)
MCP3008 DGND -> GND (black)

pot plugs into channel 0 on the 3008
"""

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'
try:
    while True:
            reading = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
            # 270 seems to be the limit.
            adjusted = int(reading)/2.70
            print "Reading: {}%".format(adjusted)

            # hang out and do nothing for a half second
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()