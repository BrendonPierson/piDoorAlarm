#!/usr/bin/env python
import time
import RPi.GPIO as io
import pygame
import smtplib

if input("would you like to send debug email, y or n?") == "y":
    myEmail = raw_input("From email")
    toEmail = raw_input("To email?")
    login = raw_input("username?")
    pw = raw_input("pw")

# set the delay so you can exit if necessary
delay = input("how much delay would you like before arming?")
for i in range(delay):
    time.sleep(1)
    print (delay - i)

print (time.strftime("%H:%M:%S"))

##### GPIO setup #####
# set the pin numbering 
io.setmode(io.BOARD)

# assign GPIO pins
alarmPin = 11
disarmPin = 13
doorPin = 37
onPin = 35
armedWdelay = 33 
armedNoDelay = 31

# doorPin => reed switch goes pin 37 to ground (brown)
    ## starts 0, goes to 1 when door opens
# alarmPin => piezo goes pin 11 to ground (yellow), 
    ## starts at 0, goes to 1 to play anoying buzz
# disarmPin => pin 13 to button to ground (green)
    ## starts 1 goes to 0 when pressed 
# armedPin => switch has the outside pins to 33 and 31 
    ## and middle pin to ground (blue)
    ## towards outside = nodelay, inside delay
# onPin => 35 is conected to 3.3v (1) or ground (0)
    ## could replace with a 


# set each pin as input or output, pull up resistors needed for switches, 
# the pull up resistor negates the need for aditional resistors in out circuit
io.setup(doorPin, io.IN, pull_up_down=io.PUD_UP)
io.setup(alarmPin, io.OUT)
io.setup(disarmPin, io.IN, pull_up_down=io.PUD_UP) # may need to put this back in
io.setup(armedWdelay, io.IN, pull_up_down=io.PUD_UP)
io.setup(armedNoDelay, io.IN, pull_up_down=io.PUD_UP)
io.setup(onPin, io.IN, pull_up_down=io.PUD_UP)
io.output(alarmPin, 0)

if io.input(onPin):
    if io.input(armedWdelay):
        print "armed with delay so we wait 5s after the door opens"
    if io.input(armedNoDelay):
        print "armed with no delay"
else:
    print "Alarm system is completely off"

##### NOISE setup #####
# itialize the pygame music player for the alarm file
pygame.mixer.init()
pygame.mixer.music.load("siren.ogg")

#start and stop functions for the music player
def musicStart():
    pygame.mixer.music.play(-1,0)
    print("music start")

def musicStop():
    pygame.mixer.music.stop()
    print("music stop")

#start and stop functions for the buzzer
def buzzerStart():
    io.output(alarmPin, 1)
    print("buzzer start")

def buzzerStop():
    io.output(alarmPin, 0)
    print("buzzer stop")

##### Main alarm function #####
def alarm():
    print("door alarm activated")
    while io.input(disarmPin):
        print("disarm pin is not activated")
        if io.input(armedWdelay):
            print "armed with delay so we wait 5s"
            time.sleep(5)
        io.output(alarmPin, 1)
        musicStart()
        if (io.input(disarmPin) == False):
            print "disarm pin is pressed"
            io.output(alarmPin, 0)
            musicStop()
            break

##### Create Event Detects #####
# door beep callback function
io.add_event_detect(doorPin, io.BOTH)
def my_callback(channel):
    print "door was open, beep beep"
    for x in range(2):
        buzzerStart()
        time.sleep(.1)
        buzzerStop()
        time.sleep(.1)
io.add_event_callback(doorPin, my_callback)

###### email function for debugging ####### 
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems

# Prompt if you would like email sent
if input("would you like to send debug email, y or n?") == "y":
    myEmail = raw_input("From email")
    toEmail = raw_input("To email?")
    login = raw_input("username?")
    pw = raw_input("pw")

#try/finally allows program to cleanup GPIO 
try:
    time.sleep(delay)
    while True:
        if io.input(doorPin) and io.input(onPin):
            print "door pin open and input is on"
            alarm()
        time.sleep(0.1)
finally:
    print (time.strftime("%H:%M:%S"))
    message = "failed at %s" % time.strftime("%H:%M:%S")
    sendemail(myEmail, toEmail, [], rPI debug, message, login, pw)
    io.cleanup()
