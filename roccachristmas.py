# -*- coding: utf-8 -*-
''' 
Rocca ChristmasPi, 2015
Developed by Peter Goodlad
Rocca Creative 2015
https://www.roccacreative.co.uk

This script analyses input from a PIR sensor attached to GPIO 7 (Pin 26) and plays a soundfile on detection

With thanks to:
http://www.modmypi.com/blog/raspberry-pi-gpio-sensing-motion-detection
https://learn.adafruit.com/playing-sounds-and-using-buttons-with-raspberry-pi?view=all
'''

import RPi.GPIO as GPIO
import time
import random
import os
from os import listdir
import re
from datetime import datetime

# Set this to true to make use of the rPI Camera if you have one set up to capture reactions
shouldUseCamera = False

# This is just to prevent the sensor triggering over and over again after each sound
arbitrarywaittime = 10

# This allows us to use GPIO numbering rather than pin numbering (which would be BOARD)
GPIO.setmode(GPIO.BCM)

# Define the pin number for easy refernce throughout
PIR_PIN = 7

# Configure the pin as an input
GPIO.setup(PIR_PIN, GPIO.IN)

# Seed Random Number Generator
random.seed()

# Get Python script location in filesystem
def getScriptPath():
		path = os.path.realpath(__file__)
		dir = os.path.dirname(path)
		return listdir(dir)

# Filter unwanted files from array
def filterFilesList(extension):
		files = getScriptPath()

		# Makeshift loop to purge files without the extension from file list
		step = 0;
		while step < len(files):
				if extension not in files[step]:
						del files[step]
						step -= 1
				step += 1
		return files

# Get seconds parameter from filename
def getSecondsFromFile(filename):
		m = re.search('(?!\s{0,},)\d{1,}(?=.mp3)', filename)
		if m:
				found = m.group(0)
				return found
		else:
				return ''

# Previously played sound
previoussound = ''

# Motion Detected! Do stuff!
def MOTION(PIR_PIN):
	# Get files each time to allow for adding sounds while script is running
	sounds = filterFilesList('.mp3')
	filename = ''
	sleeptime = ''	
	global previoussound

	# If the next sound file is the same as the last one, then try again until we get a unique sound.
	matching = True
	while matching == True:
		rnim = int(random.random() * len(sounds))
		if sounds[rnim] != previoussound:
			matching = False
			filename = sounds[rnim]
			previoussound = filename	

	# Get the number of seconds from the filename for how long we need to wait before playing more sounds
	sleeptime = int(getSecondsFromFile(filename))

	print "Motion Detected, Playing " + filename + " (" + str(sleeptime) + " seconds)"

	# Play a sound file! (In the background)
	os.system('mpg123 -q ' + filename + ' &')

	# Record a short video clip too if enabled
	if shouldUseCamera:
		videofilename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".h264"
		os.system('raspivid -o ./videos/' + videofilename + ' -hf -vf -w 1280 -h 720 -b 2000000  -t ' + str((sleeptime + arbitrarywaittime - 0.5) * 1000) +  ' -n &')

	# Wait for the sound file to finish playing before continuing 
	time.sleep(sleeptime)
	print "Sound Finished. Waiting for " + str(arbitrarywaittime) + " seconds before re-enabling sensor"
	time.sleep(arbitrarywaittime)
	print "Done...\n"
	print "Waiting for motion."

# Print Welcome Message
print "PIR Rocca Christmas 2015\n- by Peter Goodlad\n(Ctrl+C to exit)"
time.sleep(2)
print "Ready...\n"
print "Waiting for motion."

try:
	# Add an event to detect when a high voltage is detected on the input pin rather than constantly polling
	GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=MOTION, bouncetime=200)
	while 1:
		time.sleep(100)

except KeyboardInterrupt:
	print "Quit"
	GPIO.cleanup()
