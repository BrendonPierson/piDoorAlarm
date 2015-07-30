#!/usr/bin/env python
import time
import RPi.GPIO as io
import pygame
import smtplib
# import paho.mqtt.client as mqtt
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

# reed switch goes pin 37 to ground (brown)
# piezo goes pin 11 to ground (yellow)
# disarm button goes pin 13 to button to ground (green)
# armed switch has the outside pins to 33 and 31 
    ## and ground middle pin to ground (blue)
    ## towards outside = nodelay, inside delay
# onPin 35 is conected to 3.3v (1) or ground (0) 


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
##### MQTT setup #####
# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, rc):
#     print("Connected with result code "+str(rc))
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("door")

# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))

#initialize client
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# Broker ip, Port, timeout
# client.connect("192.168.8.10", 1883, 60)

#initial door closed status
# client.publish('backDoorStatus',payload='closed',qos=0,retain=False)

#subscribe to alarm armed status from openhab
# client.subscribe('alarmNoDelay',qos=0)



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
    # client.publish('backDoorStatus',payload='0',qos=0,retain=False)
    while io.input(disarmPin):
        print("disarm pin is not activated")
        if io.input(armedWdelay):
            print "armed with delay so we wait 5s"
            time.sleep(5)
        io.output(alarmPin, 1)
        musicStart()
        if (io.input(disarmPin) == False):
            print "disarm pin is pressed"
            #time.sleep(10) 
            io.output(alarmPin, 0)
            # client.publish('backDoorStatus',payload='1',qos=0,retain=False)
            musicStop()
            break

# Creates non-blocking loop for paho mqqt client to run
# client.loop_start()

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

#Turn alarm on or off callback function
# io.add_event_detect(onPin, io.BOTH)
# def armCallback (thread):
#     print "armed"
#     if io.input(onPin) == 1:
#         print "Alarm system is on"
#         if io.input(armedWdelay == 0):
#             print "You have 20 seconds before the alarm is active"
#             time.sleep(20)
#             armed()
#         else:
#             print "Alarm is activated, no delay"
#             armed()
#     else:
#         print "Alarm system is off"
# io.add_event_callback(onPin, armCallback)

#email function for debugging

 
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

if input("would you like to send debug email, y or n?") == "y":
    myEmail = "brendonpierson@gmail.com"
    toEmail = "brendonpierson@gmail.com"
    message = "failed at %s" % time.strftime("%H:%M:%S")
    login = input("username?")
    pw = input("pw")

sendemail(myEmail, toEmail, [], rPI debug, message, login, pw)

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
    io.cleanup()
