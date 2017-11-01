#!/usr/bin/env python

"""sensor array wang-jangler"""

import time

import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO
import Adafruit_SSD1306
import dht11

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

class OLEDdisplay(object):
    
    def __init__(self):
        # Raspberry Pi pin configuration:
        self.RST = None
        
        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=self.RST)
        # Initialize library.
        self.disp.begin()
        
        # Clear display.
        self.disp.clear()
        self.disp.display()
        
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        self.padding = -2
        self.top = self.padding
        self.bottom = self.height-self.padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0

        self.font = self.load_font()

    def load_font(self):
        """load a font to use"""
        # Load default font.
        try:
            return ImageFont.truetype('./slkscr.ttf', 8)
        except:
            return ImageFont.load_default()

    def drawscreen(self):
        
        # while True:
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
    
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True)
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True)
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True)
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True)
    
        # Write two lines of text.
    
        self.draw.text((self.x, self.top),       "IP: " + str(IP),  font=self.font, fill=255)
        self.draw.text((self.x, self.top+8),     str(CPU), font=self.font, fill=255)
        self.draw.text((self.x, self.top+16),    str(MemUsage),  font=self.font, fill=255)
        self.draw.text((self.x, self.top+25),    str(Disk),  font=self.font, fill=255)
    
        # Display image.
        self.disp.image(self.image)
        self.disp.display()
            # time.sleep(.1)

    def previous_state():
        pass

    def print_text(self, line):
        """Just print a line of text on the screen."""
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.draw.text((self.x, self.top), line, font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(2)
        self.disp.clear()
        self.disp.display()


class VibeSensor(object):
    def __init__(self, gpio_pin, display=None):
        """Look at a vibe sensor's output.
        Add an optional display to write onto
        
        The sensor has a pot to tune sensitivity.
        It's low by default and when vibe evets fire, it goes high to 3.3v.
        """
        self.gpio_pin = gpio_pin  # integer, BCM pin number
        self.display = display  # the display object
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.count = 0
        GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.callback, bouncetime=2000)

    def callback(self, pin):
        self.count += 1
        self.display.print_text("Shaking detected!!")
        print "Shaking detected!!!"
        time.sleep(0.5)
        self.display.drawscreen()

    def run(self):
        # import pdb;pdb.set_trace()
        while True:
            
            if GPIO.input(self.gpio_pin):
                print "HIGH input"
            else:
                print "LOW input"

            if GPIO.event_detected(self.gpio_pin):
                print "Event on pin 21!"
            time.sleep(0.1)
        
class TempSensor(object):
    def __init__(self, gpio_pin, display=None, units='farenheit'):
        self.gpio_pin = gpio_pin  # integer, BCM pin number
        self.display = display  # the display object
        GPIO.setmode(GPIO.BCM)
        self.dhtinstance = dht11.DHT11(pin=self.gpio_pin)
        self.units = units

    def run(self):
        while True:
            r = self.dhtinstance.read()
            if r.error_code == 0:
                print "Temp: {}, Humidity: {}".format(self.in_farenheit(r.temperature), r.humidity)
            time.sleep(0.5)

    def read(self):
        """
        Read the sensor, returning a dict of:
        - error_string
        - temperature
        - humidity
        """
        dht = self.dhtinstance.read()
        # if self.units == 'farenheit':
        #     dht['temperature'] = self.in_farenheit(dht.temperature)
        return dht
    
    @staticmethod
    def in_farenheit(temp_c):
        """Return a farenheit temperature value from a celsius input."""
        return temp_c * 1.8 + 32

class SensorArray(object):
    """This is all sensors, available in a single place."""
    def __init__(self):
        self.display = OLEDdisplay()
        self.thsensor = TempSensor(gpio_pin=20)
        self.vibesensor = VibeSensor(gpio_pin=21, display=self.display)
        
        # Draw the initial display
        self.display.drawscreen()

    def run(self):
        """start the sensor array"""
        my_display = OLEDdisplay()
        my_display.drawscreen()
        try:
            while True:
                th = self.thsensor.read()
                # returns 1 (error) quite often
                if th.error_code == 0:
                    print "Temp: {}, Humidity: {}".format(th.temperature, th.humidity)
                time.sleep(0.5)

        except KeyboardInterrupt:
            my_display.disp.clear()
            my_display.disp.display()
            my_display.print_text("Adios, muchacho!")
        finally:
            GPIO.cleanup()

sensors = SensorArray()
sensors.run()

